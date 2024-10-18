# matchmaking.py
from django.conf import settings
from game_manager.models import GameInstance
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
from asgiref.sync import sync_to_async
import uuid
import asyncio
import threading
import copy
import httpx
import json

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
		self.GAME_MODES = copy.deepcopy(settings.GAME_MODES)

	async def add_player_request(self, username, game_mode):
		logger.debug("Add player request")
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

	async def matchmaking_logic(self):
		for game_mode in list(self._queue.keys()):
			if game_mode not in self._queue:
				continue
				
			queue_selected = []
			for player_request in self._queue[game_mode][:]:
				queue_selected.append(player_request)
				if len(queue_selected) == self.GAME_MODES.get(game_mode).get('players'):
					await self.notify(game_mode, queue_selected)
					
					with self._queue_mutex:
						for selected in queue_selected:
							if selected in self._queue[game_mode]:
								self._queue[game_mode].remove(selected)
						
						if not self._queue[game_mode]:
							del self._queue[game_mode]
					
					break

	async def game_notify(self, game_id, admin_id, game_mode, players):
		game_service_url = settings.GAME_MODES.get(game_mode).get('service_url')
		send = {'gameId': game_id, 'adminId': admin_id, 'gameMode': game_mode, 'playersList': players}
		logger.debug(f"send: {send}")
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(game_service_url, json={
					'gameId': game_id,
					'adminId': admin_id,
					'gameMode': game_mode,
					'playersList': players
				})
			if response and response.status_code == 201 :
				return 1
			else:
				logger.debug(f'Error api request Game, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
		return 0

	async def notify(self, game_mode, queue_selected):
		logger.debug(f'New group for game_mode {game_mode}!')
		game_id = str(uuid.uuid4())
		result = game_id
		admin_id = str(uuid.uuid4())
		players = [p['username'] for p in queue_selected]
		game = await self.create_game_instance(game_id, admin_id, game_mode, players)
		if await self.game_notify(game_id, admin_id, game_mode, players) == 0:
			await self.abord_game_instance(game)
			result = None
		for player_request in queue_selected:
			username = player_request['username']
			if username in self._futures:
				future = self._futures[username]
				if not future.done():
					future.set_result({'game_id': result})
				del self._futures[username]
		if result:
			logger.debug(f'Game {game_id} created with players: {players}')
		else :
			logger.debug(f'Game {game_id} aborted')

	@sync_to_async
	def create_game_instance(self, game_id, admin_id, game_mode, players):
		return GameInstance.create_game(game_id, admin_id, game_mode, players)
	
	@sync_to_async
	def abord_game_instance(self, game):
		game.abort_game()

	async def matchmaking_loop(self):
		logger.debug("matchmaking loop started")
		while True:
			with self._is_running_mutex:
				if not self._is_running:
					break
			#logger.debug("Matchmaking loop is running...")
			await self.matchmaking_logic()
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