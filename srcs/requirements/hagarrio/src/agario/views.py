from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

# Create your views here.

def game(request):
    context = {
        'BASE_URL': settings.BASE_URL,
        'WS_URL': settings.WS_URL,
        'DEBUG': settings.DEBUG,
    }
    return render(request, 'agario/game.html', context)

def get_game_state(request):
    # Cette vue n'est plus nécessaire car l'état du jeu est géré via WebSocket
    return JsonResponse({'status': 'ok'})
