from django.urls import path
from .views import *

urlpatterns = [
	path('', index, name='index'),
	path('newtournament/', newtournament, name='newtournament'),
    path('aborttournament/', aborttournament, name='aborttournament'),
]