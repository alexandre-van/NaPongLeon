from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .game_managers.game_manager import game_manager
from .utils.logger import logger
import json

def index(request):
	return render(request, "index.html")

@csrf_exempt
def newgame(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			game_id = data.get('gameId')
			admin_id = data.get('adminId')
			game_mode = data.get('gameMode')
			modifiers = data.get('modifiers')
			players_list = data.get('playersList')
			teamsList = data.get('teamsList')
   
   
   
			special_id = data.get('special_id')
			if game_manager.add_games_room(game_id, admin_id, game_mode, modifiers, players_list, special_id, teamsList) is None:
				return JsonResponse({'error': 'Invalid game mode'}, status=406)
			logger.debug(f"Reçu: gameId={game_id}, adminId={admin_id}, gameMode={game_mode}, playersList={players_list}")
			return JsonResponse({'status': 'success'}, status=201)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def abortgame(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			game_id = data.get('gameId')
			if game_manager.abortgame(game_id) is False:
				return JsonResponse({'error': 'Invalid game id'}, status=406)
			logger.debug(f"Abort: gameId={game_id}")
			return JsonResponse({'status': 'success'}, status=204)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)
