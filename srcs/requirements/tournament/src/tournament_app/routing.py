from django.urls import re_path
from .consumers import tournamentConsumer

websocket_urlpatterns = [
    re_path(r"ws/pong/(?P<tournament_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", tournamentConsumer.as_asgi()),
    re_path(r"ws/pong/(?P<tournament_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<admin_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", tournamentConsumer.as_asgi()),
]
