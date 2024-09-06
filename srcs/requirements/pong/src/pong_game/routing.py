from django.urls import re_path
from .game_managers.game_consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/pong/$', GameConsumer.as_asgi()),
    re_path(r"ws/pong/(?P<game_id>\w+)/$", GameConsumer.as_asgi()),
]