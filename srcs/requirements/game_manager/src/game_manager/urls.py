from django.urls import path
from .views import *

urlpatterns = [
	#matchmaking
	path('matchmaking/game_mode=<str:game_mode>/', get_matchmaking, name='matchmaking'),
]