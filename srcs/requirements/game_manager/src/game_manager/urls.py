from django.urls import path, re_path
from .views import *

urlpatterns = [
	#matchmaking
	re_path(r'^matchmaking/game_mode=(?P<game_mode>.*)/$', get_in_matchmaking, name='matchmaking'),
    #game_manager
    re_path(r'^get_history/username=(?P<username>.*)/$', get_history, name='get_history'),
    re_path(r'^get_status/username=(?P<username>.*)/$', get_status, name='get_status'),
    re_path(r'^get_win_rate/username=(?P<username>.*)/game_mode=(?P<game_mode>.*)$', get_win_rate, name='get_win_rate'),
    path('create_game/', create_game, name='create_game'),
    #game_manager_api
    path('create_game_api/', create_game_api, name='create_game_api'),
    re_path(r'^get_game_data_api/(?P<game_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', get_game_data_api, name='get_game_data_api'),
]