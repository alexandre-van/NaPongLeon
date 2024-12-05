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
	logger.debug(f"request body:, {request}")
	logger.debug(f"Request body: {request.body}")
	
	# Démarre une nouvelle IA dans un thread séparé
	logger.debug("Test message - within create_ia view.")
 
	try:
		RequestBody = json.loads(request.body)
		
		# Démarrer le thread sans appeler la fonction immédiatement
		thread = Thread(target=run_ia, args=(RequestBody,))
		thread.start()
		threads.append(thread)  # Ajoute le thread à la liste pour le gérer plus tard
  
		# Réponse après démarrage du thread
		return JsonResponse({'message': 'connected to the server IA'}, status=200)

	except json.JSONDecodeError:
		logger.error("Erreur de décodage JSON dans la requête.")
		return JsonResponse({'error': 'Invalid JSON'}, status=400)

	except Exception as e:
		logger.error(f"Erreur inconnue : {str(e)}")
		return JsonResponse({'error': str(e)}, status=500)
