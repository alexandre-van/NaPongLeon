from django.urls import re_path
from .tournament_manager.consumers import TournamentConsumer

websocket_urlpatterns = [
    re_path(r"ws/tournament/(?P<tournament_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", TournamentConsumer.as_asgi()),
    re_path(r"ws/tournament/(?P<tournament_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<special_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$", TournamentConsumer.as_asgi()),
]
