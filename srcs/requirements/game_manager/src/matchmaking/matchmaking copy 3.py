# matchmaking.py
from django.conf import settings
from game_manager.game_manager import Game_manager
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
		self._futures_mutex = threading.Lock()
		self.GAME_MODES = copy.deepcopy(settings.GAME_MODES)

	async def remove_player_request(self, username):
		with self._queue_mutex:
			await Game_manager.game_manager_instance.update_player_status(username, 'inactive')
			future = await self._remove_player_request_in_queue(username)
			if future:
				future.set_result({'game_id': None})

	async def add_player_request(self, username, game_mode, modifiers, number_of_players):
		future = asyncio.Future()
		status = await Game_manager.game_manager_instance.get_player_status(username)
		if (status == 'in_queue'):
			await self.remove_player_request(username)
		elif (status != 'inactive'):
			logger.debug(f"Player {username} cannot join the matchmaking queue because their current status is '{status}'. Status must be 'inactive' to join.")
			future.set_result({'game_id': None})
			return future
		await Game_manager.game_manager_instance.update_player_status(username, 'in_queue')
		with self._futures_mutex:
				self._futures[username] = future
		queue_name = self.generate_queue_name(game_mode, modifiers, number_of_players)
		with self._queue_mutex:
			if queue_name not in self._queue:
				self._queue[queue_name] = []
			self._queue[queue_name].append({
				'username': username,
				'game_mode': game_mode,
				'modifiers': modifiers,
				'number_of_players': number_of_players,
				'time': Timer(),
			})
		return future

	def generate_queue_name(self, game_mode, modifiers_list, number_of_players):
		queue_name = ""
		queue_name += number_of_players
		for i, gm in enumerate(self.GAME_MODES):
			if gm == game_mode:
				queue_name = chr(i + ord('0'))
				if self.GAME_MODES[game_mode]['modifier_list']:
					valid_modifiers = self.GAME_MODES[game_mode]['modifier_list']
					for y, m in enumerate(valid_modifiers):
						if m in modifiers_list:
							queue_name += chr(y + ord('0'))
					break
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
					number_of_players = self.GAME_MODES.get(game_mode).get('number_of_players')
					if not number_of_players:
						number_of_players = player_request.get('number_of_players')
					if len(queue_selected) == number_of_players:
						await self.notify(game_mode, modifiers, queue_selected)
						if not self._queue[queue]:
							del self._queue[queue]
						break

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
			game_connected = await Game_manager.game_manager_instance.connect_to_game(game_id, admin_id, game_mode, modifiers, players)
		if game_connected and await self.check_futures(queue_selected):
			game = await Game_manager.game_manager_instance.create_new_game_instance(game_id, game_mode, modifiers, players)
		if game and await self.check_futures(queue_selected):
			players_connected = await self.send_result(game_id, queue_selected, game_mode)
		await self.remove_disconnected_client(queue_selected, players_connected)
		if players_connected:
			return
		# aborting
		if game_connected:
			await Game_manager.game_manager_instance.disconnect_to_game(game_id, game_mode)
			logger.debug(f'Game service {game_id} aborted')
		if game:
			await Game_manager.game_manager_instance.abord_game_instance(game)
			logger.debug(f'Game {game_id} aborted')

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

	async def send_result(self, result, queue_selected, game_mode):
		for player_request in queue_selected:
			username = player_request['username']
			with self._futures_mutex:
				if username in self._futures:
					future = self._futures[username]
					if not future.done() and not future.cancelled():
						future.set_result({
							'game_id': result,
							'service_name': self.GAME_MODES[game_mode]['service_name']
						})
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
				await Game_manager.game_manager_instance.update_player_status(username, 'inactive')
			await self._remove_player_request_in_queue(username)
			logger.debug(f"{username} is removed")

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
		with self._futures_mutex:
			queuename = self.generate_queue_name(player_request['game_mode'], player_request['modifiers'], player_request['number_of_players'])
			queue = self._queue.get(queuename)
			if queue:
				queue.remove(player_request)
			if self._futures[username]:
				future = self._futures.get(username)
				if future:
					del self._futures[username]
				return future

# Initialisation singleton
if Matchmaking.matchmaking_instance is None:
	Matchmaking.matchmaking_instance = Matchmaking()