from django.urls import re_path
from .game_managers.game_consumers import GameConsumer

websocket_urlpatterns = [
	re_path(r"ws/pong/(?P<game_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", GameConsumer.as_asgi()),
	re_path(r"ws/pong/(?P<game_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<special_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", GameConsumer.as_asgi()),
]
