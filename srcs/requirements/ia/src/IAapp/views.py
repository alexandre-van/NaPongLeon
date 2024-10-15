from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

# recevoir la game id web socket de Amery

def create_ia(request):
	return JsonResponse({'message': 'connected to the server IA'}, status=200)