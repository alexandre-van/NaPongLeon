from django.urls import path
from .views import *

urlpatterns = [
	path('', index, name='index'),
	path('newgame/', newgame, name='newgame'),
    path('abortgame/', abortgame, name='abortgame'),
]