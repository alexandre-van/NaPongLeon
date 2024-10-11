from django.shortcuts import render
from django.http import JsonResponse
from .game_state import game_state
from django.conf import settings

# Create your views here.

def game(request):
    print(f"Static root: {settings.STATIC_ROOT}")
    print(f"Static dirs: {settings.STATICFILES_DIRS}")
    print(f"Static URL: {settings.STATIC_URL}")
    return render(request, 'agario/game.html')

def get_game_state(request):
    return JsonResponse(game_state.get_state())
