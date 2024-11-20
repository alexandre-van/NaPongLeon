# views.py
from django.conf import settings
from django.http import JsonResponse
from .utils.decorators import auth_required
from matchmaking.matchmaking import Matchmaking
from .utils.logger import logger
from rest_framework import status
import asyncio

@auth_required
async def get_matchmaking(request, game_mode, username=None):
	matchmaking_instance = Matchmaking.matchmaking_instance
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=200)
	if settings.GAME_MODES.get(game_mode) is None:
		return JsonResponse({"message": "Wrong game mode"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	modifiers = request.GET.get("mods", "")
	modifier_list = modifiers.split(",") if modifiers else []
	valid_modifiers = settings.GAME_MODES.get(game_mode).get("modifier_list")
	if not all(mod in valid_modifiers for mod in modifier_list):
		return JsonResponse({"message": "Wrong game modifier"}, status=status.HTTP_406_NOT_ACCEPTABLE)
	logger.debug(f"get_matchmaking: player_request: (username: {username}, game_mode: {game_mode}, modifier: {modifier_list})")
	future = None
	try:
		future = await matchmaking_instance.add_player_request(username, game_mode, modifiers)
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