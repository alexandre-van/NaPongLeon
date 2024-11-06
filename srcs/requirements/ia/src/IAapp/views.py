# Create your views here.
from threading import Thread
from django.http import JsonResponse
from .logger import logger
from .run_ia import run_ia  # Assure-toi d'importer la tâche

# Liste pour stocker les threads
threads = []


# recevoir la game id web socket de Amery
def create_ia(request):
	 # Démarre une nouvelle IA dans un thread séparé
	logger.debug("Test message - within create_ia view.")

	thread = Thread(target=run_ia)
	thread.start()
	threads.append(thread)  # Ajoute le thread à la liste pour éventuellement le gérer plus tard
	return JsonResponse({'message': 'connected to the server IA'}, status=200)
