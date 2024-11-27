# Create your views here.
import json
from threading import Thread
from django.http import JsonResponse
from .logger import logger
from .run_ia import run_ia  # Assure-toi d'importer la tâche
from django.views.decorators.csrf import csrf_exempt
# Liste pour stocker les threads
threads = []


# recevoir la game id web socket de Amery
@csrf_exempt
def create_ia(request):
	 # Démarre une nouvelle IA dans un thread séparé
	logger.debug("Test message - within create_ia view.")

	petitchat = json.loads(request.body)
	logger.debug(f"lo petitchat {petitchat}")
	thread = Thread(target=run_ia(petitchat))
	thread.start()
	threads.append(thread)  # Ajoute le thread à la liste pour éventuellement le gérer plus tard
	return JsonResponse({'message': 'connected to the server IA'}, status=200)
