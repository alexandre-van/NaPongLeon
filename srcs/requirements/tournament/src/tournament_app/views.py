from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .tournament_manager.tournament_manager import tournament_manager
from .utils.logger import logger
import json

def index(request):
	return render(request, "index.html")

@csrf_exempt
def newtournament(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			tournament_id = data.get('gameId')
			admin_id = data.get('adminId')
			game_mode = data.get('gameMode')
			game_mode = game_mode.removesuffix("_TOURNAMENT")
			modifiers = data.get('modifiers')
			players_list = data.get('playersList')
			special_id = data.get('special_id')
			if tournament_manager.add_tournaments_room(tournament_id, admin_id, game_mode, modifiers, players_list, special_id) is None:
				return JsonResponse({'error': 'Invalid tournament mode'}, status=406)
			logger.debug(f"Reçu: tournamentId={tournament_id}, adminId={admin_id}, game_mode={game_mode}, playersList={players_list}")
			return JsonResponse({'status': 'success'}, status=201)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def aborttournament(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			tournament_id = data.get('gameId')
			if tournament_manager.aborttournament(tournament_id) is False:
				return JsonResponse({'error': 'Invalid tournament id'}, status=406)
			logger.debug(f"Abort: tournamentId={tournament_id}")
			return JsonResponse({'status': 'success'}, status=204)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)