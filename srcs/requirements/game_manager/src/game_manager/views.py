# views.py
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .utils.decorators import auth_required, async_csrf_exempt
from .game_manager import Game_manager
from matchmaking.matchmaking import Matchmaking
from .utils.logger import logger
from rest_framework import status
import asyncio
import json

@async_csrf_exempt
@auth_required
async def get_history(request, username=None):
	if request.method != "GET":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	game_manager_instance = Game_manager.game_manager_instance
	if game_manager_instance is None:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	try :
		await game_manager_instance.create_new_player_instance(username)
		game_history = await game_manager_instance.get_game_history(username)
		return JsonResponse({'status': 'success', 'game_history': game_history, 'username': username}, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error(f"Error in get_game_history for user {username}: {str(e)}")
		return JsonResponse({"message": "GameManager error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
@async_csrf_exempt
@auth_required
async def get_status(request, username=None):
	if request.method != "GET":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	game_manager_instance = Game_manager.game_manager_instance
	if game_manager_instance is None:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	try :
		await game_manager_instance.create_new_player_instance(username)
		data = await game_manager_instance.get_user_status(username)
		return JsonResponse({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error(f"Error in get_game_history for user {username}: {str(e)}")
		return JsonResponse({"message": "GameManager error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
@async_csrf_exempt
@auth_required
async def get_win_rate(request, username=None, game_mode=None):
	if request.method != "GET":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	game_manager_instance = Game_manager.game_manager_instance
	if game_manager_instance is None:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	try :
		await game_manager_instance.create_new_player_instance(username)
		data = await game_manager_instance.get_user_win_rate(username, game_mode)
		return JsonResponse({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error(f"Error in get_game_history for user {username}: {str(e)}")
		return JsonResponse({"message": "GameManager error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
@async_csrf_exempt
@auth_required
async def get_in_matchmaking(request, game_mode, username=None):
	if request.method != "GET":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	game_manager_instance = Game_manager.game_manager_instance
	matchmaking_instance = Matchmaking.matchmaking_instance
	if game_manager_instance is None:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	if game_mode == "":
		return await get_out_matchmaking(username, game_manager_instance, matchmaking_instance)
	if settings.GAME_MODES.get(game_mode) is None:
		return JsonResponse({"message": "Wrong game mode"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	modifiers = request.GET.get("mods", "")
	number_of_players = request.GET.get("playernumber", "")
	modifier_list = game_manager_instance.parse_modifier(modifiers, game_mode)
	if modifier_list is None:
		return JsonResponse({"message": "Wrong game modifier"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	logger.debug(f"get_matchmaking: player_request: (username: {username}, game_mode: {game_mode}, modifier: {modifier_list})")
	future = None
	try:
		await game_manager_instance.create_new_player_instance(username)
		future = await matchmaking_instance.add_player_request(username, game_mode, modifier_list, number_of_players)
		game_data = await asyncio.wait_for(future, timeout=3600)
		return JsonResponse({"message": "Matchmaking succeeded", "data": game_data}, status=status.HTTP_200_OK)
	except asyncio.TimeoutError:
		if not future.done():
			future.cancel()
		logger.error(f"Matchmaking timed out for user {username}")
		return JsonResponse({"message": "Matchmaking timed out"}, status=status.HTTP_408_REQUEST_TIMEOUT)
	except Exception as e:
		logger.error(f"Error in matchmaking for user {username}: {str(e)}")
		return JsonResponse({"message": "Matchmaking error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
async def get_out_matchmaking(username, game_manager_instance, matchmaking_instance):
	logger.debug("get_out_matchmaking")
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	try:
		await game_manager_instance.create_new_player_instance(username)
		await matchmaking_instance.remove_player_request(username)
		return JsonResponse({"message": "Get out matchmaking succeeded"}, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error(f"Error to get out matchmaking for user {username}: {str(e)}")
		return JsonResponse({"message": "Matchmaking error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@async_csrf_exempt
@auth_required
async def create_game(request, username=None):
	game_manager_instance = Game_manager.game_manager_instance
	if game_manager_instance is None:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	await game_manager_instance.create_new_player_instance(username)
	return await create_game_api(request, username)

@async_csrf_exempt
async def create_game_api(request, username=None):
	if request.method == 'POST':
		try:
			game_manager_instance = Game_manager.game_manager_instance
			if game_manager_instance is None:
				return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			# json LOADS
			data = json.loads(request.body)
			game_mode = data.get('gameMode')
			modifiers = data.get('modifiers')
			players_list = data.get('playersList')
			teams_list = data.get('teamsList')
			ia_authorizes = data.get('ia_authorizes')
			special_id = data.get('special_id')
			logger.debug(f"Reçu: game_mode={game_mode}, modifiers={modifiers}, players_list={players_list}, teams={teams_list}, ai={ia_authorizes}")
			game_data = await game_manager_instance.create_game(game_mode, modifiers, players_list, teams_list,
				ia_authorizes if ia_authorizes else False,
				special_id if special_id else [])
			# pars players
			if game_data:
				return JsonResponse({'status': 'success', 'data': game_data}, status=status.HTTP_201_CREATED)
			else:
				return JsonResponse({'error': 'Invalid game information'}, status=status.HTTP_406_NOT_ACCEPTABLE)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
	
@async_csrf_exempt
async def get_game_data_api(request, game_id):
	if request.method != "GET":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	game_manager = Game_manager.game_manager_instance
	if not game_manager:
		return JsonResponse({"message": "Game Manager is not initialised"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	try:
		game_data = await game_manager.get_game_data(game_id)
		
		if not game_data:
			return JsonResponse({"error": "Game not found"}, status=404)
		
		return JsonResponse({"game_data": game_data}, status=200)
	except ObjectDoesNotExist:
		return JsonResponse({"error": "Game not found"}, status=404)
	except Exception as e:
		return JsonResponse({"error": str(e)}, status=500)