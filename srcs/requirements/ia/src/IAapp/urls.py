
from django.urls import path, include
from .views import create_ia

urlpatterns = [
    path('create_ia/', create_ia, name='create_ia'),
]
