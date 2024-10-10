from django.shortcuts import render
from django.http import JsonResponse
from .game_state import game_state

# Create your views here.

def game(request):
    return render(request, 'agario/game.html')

def get_game_state(request):
    return JsonResponse(game_state.get_state())
