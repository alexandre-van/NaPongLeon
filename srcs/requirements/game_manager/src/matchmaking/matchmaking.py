# matchmaking.py
from django.conf import settings
from django.db import transaction
from game_manager.game_manager import Game_manager
from game_manager.models import GameInstance, Player
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
from admin_manager.admin_manager import AdminManager
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
		self._futures_mutex = threading.Lock()
		self.GAME_MODES = copy.deepcopy(settings.GAME_MODES)

	async def remove_player_request(self, username):
		with self._queue_mutex:
			await self._remove_player_request_in_queue(username)

	async def add_player_request(self, username, game_mode, modifiers):
		logger.debug("Add player request")
		future = asyncio.Future()
		status = await self.get_player_status(username)
		if (status != 'inactive'):
			logger.debug(f"Player {username} cannot join the matchmaking queue because their current status is '{status}'. Status must be 'inactive' to join.")
			future.set_result({'game_id': None})
			return future
		await self.update_player_status(username, 'in_queue')
		with self._futures_mutex:
				self._futures[username] = future
		queue_name = self.generate_queue_name(game_mode, modifiers)
		with self._queue_mutex:
			if queue_name not in self._queue:
				self._queue[queue_name] = []
			self._queue[queue_name].append({
				'username': username,
				'game_mode': game_mode,
				'modifiers': modifiers,
				'time': Timer(),
			})
		return future

	def generate_queue_name(self, game_mode, modifiers_list):
		queue_name = ""
		for i, gm in enumerate(self.GAME_MODES):
			if gm == game_mode:
				queue_name = chr(i + ord('0'))
				valid_modifiers = self.GAME_MODES[game_mode]['modifier_list']
				for y, m in enumerate(valid_modifiers):
					if m in modifiers_list:
						queue_name += chr(y + ord('0'))
					logger.debug(f"{m}")
				break
		logger.debug(f"queue_name : {queue_name}")
		return queue_name


	async def matchmaking_logic(self):
		with self._queue_mutex:
			for queue in list(self._queue.keys()):
				if queue not in self._queue:
					continue
				await self.remove_disconnected_client(self._queue[queue], False)
				queue_selected = []
				for player_request in self._queue[queue][:]:
					queue_selected.append(player_request)
					game_mode = player_request.get('game_mode')
					modifiers = player_request.get('modifiers')
					if len(queue_selected) == self.GAME_MODES.get(game_mode).get('number_of_players'):
						await self.notify(game_mode, modifiers, queue_selected)
						if not self._queue[queue]:
							del self._queue[queue]
						break

	async def game_notify(self, game_id, admin_id, game_mode, modifiers, players):
		game_service_url = settings.GAME_MODES.get(game_mode).get('service_url_new_game')
		send = {'gameId': game_id, 'adminId': admin_id, 'gameMode': game_mode, 'playersList': players}
		logger.debug(f"send to {game_service_url}: {send}")
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(game_service_url, json={
					'gameId': game_id,
					'adminId': admin_id,
					'gameMode': game_mode,
					'modifiers': modifiers,
					'playersList': players
				})
			if response and response.status_code == 201 :
				return True
			else:
				logger.debug(f'Error api request Game, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
		return False

	async def game_abort_notify(self, game_id, game_mode):
		game_service_url = settings.GAME_MODES.get(game_mode).get('service_url_abort_game')
		send = {'gameId': game_id}
		logger.debug(f"send to {game_service_url}: {send}")
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(game_service_url, json={
					'gameId': game_id
				})
			if response and response.status_code == 204 :
				return True
			else:
				logger.debug(f'Error api request Game, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"Authentication service error: {str(e)}")
		return False

	async def notify(self, game_mode, modifiers, queue_selected):
		logger.debug(f'New group for game_mode {game_mode}!')
		game_id = str(uuid.uuid4())
		admin_id = str(uuid.uuid4())
		players = [p['username'] for p in queue_selected]
		game = None
		game_connected = False
		players_connected = False
		# new game
		if await self.check_futures(queue_selected):
			game_connected = await self.connect_to_game(game_id, admin_id, game_mode, modifiers, players)
		if game_connected and await self.check_futures(queue_selected):
			game = await self.create_new_game(game_id, game_mode, players)
		if game and await self.check_futures(queue_selected):
			players_connected = await self.send_result(game_id, queue_selected)
		await self.remove_disconnected_client(queue_selected, players_connected)
		if players_connected:
			return
		# aborting
		if game_connected:
			await self.disconnect_to_game(game_id, game_mode)
			logger.debug(f'Game service {game_id} aborted')
		if game:
			await self.abord_game_instance(game)
			logger.debug(f'Game {game_id} aborted')

	async def connect_to_game(self, game_id, admin_id, game_mode, modifiers, players):
		is_game_notified = await self.game_notify(game_id, admin_id, game_mode, modifiers, players)
		if is_game_notified:
			logger.debug(f'Game service {game_id} created with players: {players}')
			AdminManager.admin_manager_instance.start_connections(game_id, admin_id, game_mode)
			return True
		else:
			return False

	async def disconnect_to_game(self, game_id, game_mode):
		is_game_notified = await self.game_abort_notify(game_id, game_mode)
		if is_game_notified:
			logger.debug(f'Game service {game_id} aborted')
			return True
		else:
			logger.debug(f'Game serice {game_id} was not aborted')
			return False

	async def check_futures(self, queue_selected):
		for player_request in queue_selected:
			username = player_request['username']
			with self._futures_mutex:
				if username in self._futures:
					future = self._futures[username]
					if not future.done() and not future.cancelled():
						continue
			return None
		return True

	async def send_result(self, result, queue_selected):
		for player_request in queue_selected:
			username = player_request['username']
			with self._futures_mutex:
				if username in self._futures:
					future = self._futures[username]
					if not future.done() and not future.cancelled():
						future.set_result({'game_id': result})
						continue
			logger.debug(f"return none at {username}")
			return None
		return True

	async def remove_disconnected_client(self, queue, players_connected):
		for player_request in queue:
			username = player_request['username']
			if not players_connected:
				with self._futures_mutex:
					if username in self._futures:
						future = self._futures[username]
						if not future.done() and not future.cancelled():
							continue
				await self.update_player_status(username, 'inactive')
			await self._remove_player_request_in_queue(username)
			logger.debug(f"{username} is removed")

	async def create_new_game(self, game_id, game_mode, players):
		game = await self.create_game_instance(game_id, game_mode, players)
		if game:
			for username in players:
				await self.update_player_status(username, 'pending')
			return game
		else:
			return None
	
	async def change_all_players_status(self, players, status):
		for username in players:
			await self.update_player_status(username, status)

	@sync_to_async
	def create_game_instance(self, game_id, game_mode, players):
		with transaction.atomic():
			game_instance = GameInstance.create_game(game_id, game_mode, players)
			Game_manager.game_manager_instance.add_new_game(game_id)
			return game_instance
		return None

	@sync_to_async
	def get_player_status(self, username):
		with transaction.atomic():
			player = Player.get_or_create_player(username)
			return player.status
		return None

	@sync_to_async
	def update_player_status(self, username, status):
		with transaction.atomic():
			player = Player.get_or_create_player(username)
			player.update_status(status)

	@sync_to_async
	def abord_game_instance(self, game):
		with transaction.atomic():
			game.abort_game()


	# LOOP


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
			return
		with self._futures_mutex:
			queue = self.generate_queue_name(player_request['game_mode'], player_request['modifiers'])
			self._queue[queue].remove(player_request)
			if self._futures[username]:
				del self._futures[username]

# Initialisation singleton
if Matchmaking.matchmaking_instance is None:
	Matchmaking.matchmaking_instance = Matchmaking()