from django.urls import re_path
from .game_manager_project.consumers import game_manager_projectConsumer

websocket_urlpatterns = [
    re_path(r'ws/pong/$', game_manager_projectConsumer.as_asgi()),
    re_path(r"ws/pong/(?P<game_id>\w+)/$", game_manager_projectConsumer.as_asgi()),
]