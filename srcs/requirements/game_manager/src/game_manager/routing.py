from django.urls import re_path
from .private_room.consumer import PrivateRoomConsumer

websocket_urlpatterns = [
	re_path(r"^ws/game_manager/join_private/(?P<username>\w{1,20})/$", PrivateRoomConsumer.as_asgi()),
	re_path(r"^ws/game_manager/create_private/$", PrivateRoomConsumer.as_asgi()),
]
