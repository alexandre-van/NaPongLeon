from django.conf import settings
from django.http import JsonResponse
from .utils.decorators import auth_required
from matchmaking.matchmaking import Matchmaking
from .utils.logger import logger
from asgiref.sync import sync_to_async
import asyncio

@auth_required
async def get_matchmaking(request, game_mode, username=None):
	matchmaking_instance = Matchmaking.matchmaking_instance
	if matchmaking_instance is None:
		return JsonResponse({"message": "Matchmaking is not initialised"}, status=200)

	logger.debug('get_matchmaking')
	logger.debug(f'game_mode_request = {game_mode}')
	logger.debug(f'number of players required  = {settings.GAME_MODES.get(game_mode)}')
	logger.debug(f'username = {username}')

	# Appel de méthode bloquante avec sync_to_async
	await sync_to_async(matchmaking_instance.add_player_request)(username, game_mode)

	await asyncio.sleep(10)
	return JsonResponse({"message": "Matchmaking succeeded"}, status=200)
