from django.urls import path
from .views import *

urlpatterns = [
    path('matchmaking/', matchmaking, name='matchmaking'),
]