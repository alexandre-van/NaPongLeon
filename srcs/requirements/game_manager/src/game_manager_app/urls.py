from django.urls import path
from .views import *

urlpatterns = [
    path('api/game_manager/matchmaking', matchmaking.as_view(), name='matchmaking'),
]