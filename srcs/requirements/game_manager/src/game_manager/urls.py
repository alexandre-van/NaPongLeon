from django.urls import re_path
from .views import *

urlpatterns = [
	#matchmaking
	re_path(r'^matchmaking/game_mode=(?P<game_mode>.*)/$', get_in_matchmaking, name='matchmaking'),
]