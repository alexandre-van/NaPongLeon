from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .consumers import GameConsumer
import json

# Create your views here.

def game(request):
    return render(request, 'game.html')

@csrf_exempt
def newgame(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			game_id = data.get('gameId')
			admin_id = data.get('adminId')
			players_list = data.get('playersList')
			GameConsumer.create_new_game(game_id, admin_id, players_list)
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
			if GameConsumer.abortgame(game_id) is False:
				return JsonResponse({'error': 'Invalid game id'}, status=406)
			return JsonResponse({'status': 'success'}, status=204)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)


#def get_game_state(request):
    # Cette vue n'est plus nécessaire car l'état du jeu est géré via WebSocket
#    return JsonResponse({'status': 'ok'})
