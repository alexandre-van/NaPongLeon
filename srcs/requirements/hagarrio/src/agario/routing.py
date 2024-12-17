from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/hagarrio/$', consumers.GameConsumer.as_asgi()),
	re_path(r"ws/hagarrio/(?P<game_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<special_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", consumers.GameConsumer.as_asgi()),
]

