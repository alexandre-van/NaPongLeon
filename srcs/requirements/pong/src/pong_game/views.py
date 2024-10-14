from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .game_managers.game_manager import game_manager
from .utils.logger import logger
import json

def index(request):
	return render(request, "index.html")

@csrf_exempt
def newgame(request):
	if request.method == 'POST':
		try:
			# Récupération des données JSON envoyées dans le corps de la requête
			data = json.loads(request.body)

			# Extraction des informations
			game_id = data.get('gameId')
			admin_id = data.get('adminId')
			game_mode = data.get('gameMode')
			players_list = data.get('playersList')
			if game_manager.add_waiting_room(game_id, admin_id, game_mode, players_list) is None:
				return JsonResponse({'error': 'Invalid game mode'}, status=406)
			# Debug pour vérifier les données reçues
			logger.debug(f"Reçu: gameId={game_id}, adminId={admin_id}, gameMode={game_mode}, playersList={players_list}")

			# Logique de gestion de la création du jeu ici

			# Répondre avec un succès
			return JsonResponse({'status': 'success'}, status=201)

		except json.JSONDecodeError:
			# Gérer une erreur de décodage JSON
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		# Réponse pour les autres méthodes HTTP (par exemple GET)
		return JsonResponse({'error': 'Invalid request method'}, status=405)
