# matchmaking.py
from django.conf import settings
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
import uuid
import asyncio
import threading
import copy

class Matchmaking:
	matchmaking_instance = None
	
	def __init__(self):
		logger.debug("Matchmaking init...")
		self._is_running = False
		self._task = None
		self._is_running_mutex = threading.Lock()
		self._queue = {}
		self._queue_mutex = threading.Lock()
		self._futures = {}
		self.GAME_MODES = copy.copy(settings.GAME_MODES)

	async def add_player_request(self, username, game_mode):
		logger.debug("Add player request")
		# Créer le future dans le contexte async
		future = asyncio.Future()
		self._futures[username] = future
		
		with self._queue_mutex:
			if game_mode not in self._queue:
				self._queue[game_mode] = []
			self._queue[game_mode].append({
				'username': username,
				'time': Timer(),
				'future': future
			})
		return future
	
	async def add_player_request(self, username, game_mode):
		logger.debug("Add player request")
		# Créer le future dans le contexte async
		future = asyncio.Future()
		self._futures[username] = future
		
		with self._queue_mutex:
			if game_mode not in self._queue:
				self._queue[game_mode] = []
			self._queue[game_mode].append({
				'username': username,
				'time': Timer(),
				'future': future
			})
		return future

	def matchmaking_logic(self):
		for game_mode in list(self._queue.keys()):  # Utilisez une copie des clés
			if game_mode not in self._queue:
				continue
				
			queue_selected = []
			for player_request in self._queue[game_mode][:]:  # Utilisez une copie de la liste
				queue_selected.append(player_request)
				if len(queue_selected) == self.GAME_MODES.get(game_mode):
					# Notifier les joueurs sélectionnés
					self.notify_players(queue_selected)
					
					# Retirer les joueurs sélectionnés de la file d'attente
					for selected in queue_selected:
						if selected in self._queue[game_mode]:
							self._queue[game_mode].remove(selected)
					
					if not self._queue[game_mode]:
						del self._queue[game_mode]
					
					break

	def notify_players(self, queue_selected):
		result = {
			"game_id": str(uuid.uuid4()),
			"players": [p['username'] for p in queue_selected]
		}
		logger.debug(f'New group : {result}')
		for player_request in queue_selected:
			username = player_request['username']
			if username in self._futures:
				future = self._futures[username]
				if not future.done():
					future.set_result(result)
				del self._futures[username]

	async def matchmaking_loop(self):
		logger.debug("matchmaking loop started")
		while True:
			with self._is_running_mutex:
				if not self._is_running:
					break
			logger.debug("Matchmaking loop is running...")
			with self._queue_mutex:
				self.matchmaking_logic()
			await asyncio.sleep(1)

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

# Initialisation singleton
if Matchmaking.matchmaking_instance is None:
	Matchmaking.matchmaking_instance = Matchmaking()