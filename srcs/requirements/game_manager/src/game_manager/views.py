# views.py
from django.conf import settings
from django.http import JsonResponse
from .utils.decorators import auth_required
from .game_manager import Game_manager
from matchmaking.matchmaking import Matchmaking
from .utils.logger import logger
from rest_framework import status
import asyncio

@auth_required
async def get_in_matchmaking(request, game_mode, username=None):
	if game_mode is "":
		return await get_out_matchmaking(username)
	matchmaking_instance = Matchmaking.matchmaking_instance
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=200)
	if settings.GAME_MODES.get(game_mode) is None:
		return JsonResponse({"message": "Wrong game mode"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	modifiers = request.GET.get("mods", "")
	modifier_list = Game_manager.game_manager_instance.parse_modifier(modifiers, game_mode)
	if modifier_list is None:
		return JsonResponse({"message": "Wrong game modifier"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	logger.debug(f"get_matchmaking: player_request: (username: {username}, game_mode: {game_mode}, modifier: {modifier_list})")
	future = None
	try:
		future = await matchmaking_instance.add_player_request(username, game_mode, modifier_list)
		game_data = await asyncio.wait_for(future, timeout=3600)
		return JsonResponse({"message": "Matchmaking succeeded", "data": game_data}, status=status.HTTP_200_OK)
	except asyncio.TimeoutError:
		if not future.done():
			future.cancel()
		logger.error(f"Matchmaking timed out for user {username}")
		return JsonResponse({"message": "Matchmaking timed out"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
	except Exception as e:
		logger.error(f"Error in matchmaking for user {username}: {str(e)}")
		return JsonResponse({"message": "Matchmaking error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
async def get_out_matchmaking(username):
	matchmaking_instance = Matchmaking.matchmaking_instance
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=200)
	try:
		await matchmaking_instance.remove_player_request(username)
		return JsonResponse({"message": "Get out matchmaking succeeded"}, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error(f"Error to get out matchmaking for user {username}: {str(e)}")
		return JsonResponse({"message": "Matchmaking error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)