import threading
import websockets
import asyncio
from django.db import transaction
from django.conf import settings
from game_manager.utils.logger import logger
from asgiref.sync import sync_to_async

class AdminManager:
	admin_manager_instance = None

	def __init__(self):
		self.connections = {}
		self.threads = []  # Liste pour garder la trace des threads

	def connect_to_game(self, game_id, admin_id, ws_url):
		# Démarre un nouvel event loop pour chaque thread
		logger.debug(f'new thread created to {ws_url} !')
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(self._handle_websocket(game_id, ws_url))
	
	async def _handle_websocket(self, game_id, ws_url):
		logger.debug(f'thread in game : {game_id} is running...')
		async with websockets.connect(ws_url) as websocket:
			self.connections[game_id] = websocket
			# Écouter en boucle les événements en temps réel
			while True:
				#message = await websocket.recv()
				pass
			#	await self.handle_message(game_id, message)
	
	@sync_to_async
	def handle_message(self, game_id, message):
		# Gérer les messages reçus, exemple : mise à jour de la base de données
		#with transaction.atomic():
		#	logger.debug(f"Game {game_id}: Received message: {message}")
		#	# Logique de mise à jour du score, statut de joueur, etc.
			pass

	def start_connections(self, game_id, admin_id, game_mode):
		# Extraire les informations de la partie
		ws_url = settings.GAME_MODES.get(game_mode).get('service_ws') + game_id + '/' + admin_id + '/'
		logger.debug(f'start_new_connection ws - game_id = {game_id}, admin_id = {admin_id}, ws_url = {ws_url}')
		# Créer un thread pour la connexion WebSocket
		thread = threading.Thread(target=self.connect_to_game, args=(game_id, admin_id, ws_url))
		thread.start()

		# Ajouter le thread à la liste des threads
		self.threads.append(thread)

	def close_all(self):
		# Rejoindre tous les threads pour s'assurer qu'ils se terminent proprement
		for thread in self.threads:
			thread.join()  # Attendre que chaque thread se termine
		logger.debug("Tous les threads sont terminés, fermeture du programme.")

if AdminManager.admin_manager_instance is None:
	AdminManager.admin_manager_instance = AdminManager()
