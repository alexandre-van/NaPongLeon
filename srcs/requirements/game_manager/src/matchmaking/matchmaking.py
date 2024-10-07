from django.conf import settings
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
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
		self.GAME_MODES = copy.copy(settings.GAME_MODES)

	def add_player_request(self, username, game_mode):
		logger.debug("Add player request")
		with self._queue_mutex:
			if game_mode not in self._queue:
				self._queue[game_mode] = []
			self._queue[game_mode].append({
				'username': username,
				'time': Timer()
			})

	def matchmaking_logic(self):
		for game_mode in self._queue:
			queue_selected = []
			for player_request in self._queue[game_mode]:
				queue_selected.append(player_request)
				if len(queue_selected) == self.GAME_MODES.get(game_mode):
					break
			if len(queue_selected) != self.GAME_MODES.get(game_mode):
				continue
			for player_request_selected in queue_selected:
				self._queue[game_mode].remove(player_request_selected)
			logger.debug(f"New group ['game_mode': {game_mode}, 'players': {queue_selected}]")

			

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

		self._task = asyncio.current_task()
		try:
			await self.matchmaking_loop()
			logger.debug("Matchmaking stopped.")
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

if Matchmaking.matchmaking_instance == None:
	Matchmaking.matchmaking_instance = Matchmaking()