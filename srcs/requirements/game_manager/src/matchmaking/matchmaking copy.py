# matchmaking.py
from django.conf import settings
from game_manager.game_manager import Game_manager
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
import uuid
import json
import threading
import copy
import asyncio

# matchmaking.py
class Matchmaking:
	matchmaking_instance = None
	
	def __init__(self):
		logger.debug("Matchmaking init...")
		self._queue = {}
		self._queue_mutex = threading.Lock()
		self.GAME_MODES = copy.deepcopy(settings.GAME_MODES)

	async def remove_player_request(self, username):
		await Game_manager.game_manager_instance.update_player_status(username, 'inactive')
		with self._queue_mutex:
			await self._remove_player_request_in_queue(username)

	async def add_player_to_queue(self, username, game_mode, modifiers, number_of_players, websocket):
		status = await Game_manager.game_manager_instance.get_player_status(username)
		if status == 'in_queue':
			await self.remove_player_request(username)
		elif status != 'inactive':
			logger.debug(f"Player {username} cannot join queue, status is '{status}'")
			await websocket.send(json.dumps({
				'error': f"Cannot join queue with status '{status}'"
			}))
			return

		await Game_manager.game_manager_instance.update_player_status(username, 'in_queue')
		queue_name = self.generate_queue_name(game_mode, modifiers, number_of_players)
		
		with self._queue_mutex:
			if queue_name not in self._queue:
				self._queue[queue_name] = []
			self._queue[queue_name].append({
				'username': username,
				'game_mode': game_mode,
				'modifiers': modifiers,
				'number_of_players': number_of_players,
				'websocket': websocket,
				'time': Timer(),
			})
		
		# Notifier le joueur qu'il est en file d'attente
		await websocket.send(json.dumps({
			'status': 'queued',
			'message': 'Joined matchmaking queue'
		}))

	async def matchmaking_logic(self):
		with self._queue_mutex:
			for queue in list(self._queue.keys()):
				if queue not in self._queue:
					continue
				
				queue_selected = []
				for player_request in self._queue[queue][:]:
					queue_selected.append(player_request)
					game_mode = player_request.get('game_mode')
					number_of_players = (self.GAME_MODES.get(game_mode, {})
									   .get('number_of_players') or 
									   player_request.get('number_of_players'))
					
					if len(queue_selected) == number_of_players:
						await self.create_game(game_mode, 
											 player_request.get('modifiers'), 
											 queue_selected)
						if not self._queue[queue]:
							del self._queue[queue]
						break

	async def create_game(self, game_mode, modifiers, queue_selected):
		game_id = str(uuid.uuid4())
		admin_id = str(uuid.uuid4())
		players = [p['username'] for p in queue_selected]
		
		try:
			# Créer la partie
			game_connected = await Game_manager.game_manager_instance.connect_to_game(
				game_id, admin_id, game_mode, modifiers, players)
			
			if not game_connected:
				raise Exception("Failed to connect to game")
				
			game = await Game_manager.game_manager_instance.create_new_game_instance(
				game_id, game_mode, modifiers, players)
				
			if not game:
				raise Exception("Failed to create game instance")

			# Notifier tous les joueurs
			for player in queue_selected:
				websocket = player['websocket']
				await websocket.send(json.dumps({
					'status': 'game_found',
					'game_id': game_id,
					'service_name': self.GAME_MODES[game_mode]['service_name']
				}))
				
			# Retirer les joueurs de la file
			for player in queue_selected:
				await self.remove_player_request(player['username'])
				
		except Exception as e:
			logger.error(f"Error creating game: {str(e)}")
			# Nettoyer en cas d'erreur
			if 'game_connected' in locals():
				await Game_manager.game_manager_instance.disconnect_to_game(
					game_id, game_mode)
			if 'game' in locals():
				await Game_manager.game_manager_instance.abord_game_instance(game)
			
			# Notifier les joueurs de l'échec
			for player in queue_selected:
				websocket = player['websocket']
				await websocket.send(json.dumps({
					'error': 'Failed to create game'
				}))

	# LOOP

	async def matchmaking_loop(self):
		logger.debug("matchmaking loop started")
		while True:
			with self._is_running_mutex:
				if not self._is_running:
					break
			await self.matchmaking_logic()
			await asyncio.sleep(0.5)

	async def start_matchmaking_loop(self):
		with self._is_running_mutex:
			self._is_running = True
		self._task = asyncio.create_task(self.matchmaking_loop())
		try:
			await self._task
		except asyncio.CancelledError:
			logger.debug("Matchmaking loop has been cancelled.")
		finally:
			logger.debug("Exiting matchmaking loop.")

	def stop_matchmaking(self):
		logger.debug("Matchmaking stopping...")
		with self._is_running_mutex:
			self._is_running = False
			if self._task:
				self._task.cancel()

	# unproteged

	async def _get_player_request(self, username):
		for queue in list(self._queue.keys()):
			for player_request in self._queue[queue][:]:
				if player_request['username'] == username:
					return player_request
		return None

	async def _remove_player_request_in_queue(self, username):
		player_request = await self._get_player_request(username)
		if player_request is None:
			return None
		queuename = self.generate_queue_name(player_request['game_mode'], player_request['modifiers'], player_request['number_of_players'])
		queue = self._queue.get(queuename)
		if queue:
			queue.remove(player_request)

# Initialisation singleton
if Matchmaking.matchmaking_instance is None:
	Matchmaking.matchmaking_instance = Matchmaking()