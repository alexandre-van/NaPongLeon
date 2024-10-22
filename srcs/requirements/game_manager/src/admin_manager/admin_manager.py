import threading
import websockets
import asyncio
from game_manager.models import GameInstance, Player
from django.db import transaction
from django.conf import settings
from game_manager.utils.logger import logger
from asgiref.sync import sync_to_async
import json

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
		users = {
			'players': [],
			'spectator': []
		}
		async with websockets.connect(ws_url) as websocket:
			logger.debug(f"Websocket connected : {ws_url}")
			#self.admin_connected(game_id)
			self.connections[game_id] = websockets
			try:
				async for message in websocket:
					message_dict = json.loads(message)
					await self.handle_message(game_id, message_dict, users)
			except websockets.exceptions.ConnectionClosedOK:
				logger.debug("WebSocket connection closed normally (1000 OK).")
			except websockets.exceptions.ConnectionClosedError as e:
				logger.error(f"WebSocket closed with error: {e}")
			except json.JSONDecodeError as e:
				logger.error(f"Failed to decode message: {e}")

	#@sync_to_async
	#def admin_connected(self, game_id):
	#	game_instance = GameInstance.get_game(game_id)
	#	if not game_instance:
	#		return
	#	with transaction.atomic():
	#		game_instance.update_status('waiting')

	@sync_to_async
	def handle_message(self, game_id, message, users):
		logger.debug(f"Game {game_id}: Received message: {message}")
		type = message.get("type")
		if type == "export_status":
			status = message.get("status")
			if status == 'loading':
				for username in users['players']:
					with transaction.atomic():
						player = Player.get_or_create_player(username)
						player.update_status('loading_game')
			if status == 'in_progress':
				for username in users['players']:
					with transaction.atomic():
						player = Player.get_or_create_player(username)
						player.update_status('in_game')
			if status == 'aborted' or status == 'finished':
				for username in users['players']:
					with transaction.atomic():
						player = Player.get_or_create_player(username)
						player.update_status('inactive')
				for username in users['spectator']:
					with transaction.atomic():
						spectator = Player.get_or_create_player(username)
						spectator.update_status('inactive')
			game_instance = GameInstance.get_game(game_id)
			if not game_instance:
				return
			with transaction.atomic():
				game_instance.update_status(status)
		elif type == "export_teams":
			game_instance = GameInstance.get_game(game_id)
			if not game_instance:
				return
			teams = message.get("teams")
			with transaction.atomic():
				game_instance.update_status(status)
				for team in teams:
					for player in teams[team]:
						game_instance.add_player_to_team(player, team)
		elif type == "update_score":
			game_instance = GameInstance.get_game(game_id)
			if not game_instance:
				return
			team_name = message.get("team_name")
			score = message.get("score")
			with transaction.atomic():
				game_instance.update_score(team_name, score)
		elif type == "player_connection":
			username = message.get("username")
			users['players'].append(username)
			with transaction.atomic():
				player = Player.get_or_create_player(username)
				if player:
					player.update_status('waiting_for_players')
		elif type == "spectator_connection":
			username = message.get("username")
			users['spectator'].append(username)
			with transaction.atomic():
				player = Player.get_or_create_player(username)
				if player:
					player.update_status('spectate')
		elif type == "player_disconnection":
			username = message.get("username")
			users['players'].remove(username)
			with transaction.atomic():
				player = Player.get_or_create_player(username)
				if player:
					player.update_status('inactive')
		elif type == "spectator_disconnection":
			username = message.get("username")
			users['spectator'].remove(username)
			with transaction.atomic():
				player = Player.get_or_create_player(username)
				if player:
					player.update_status('inactive')
					
			

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
