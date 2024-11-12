from django.conf import settings
from .models import Player, GameInstance, GamePlayer
from .utils.logger import logger
from .private_room.private_room import PrivateRoom, GenerateUsername
from .utils.timer import Timer
from django.apps import apps
from django.db import connection
from asgiref.sync import sync_to_async
from django.db import transaction
import threading
import asyncio
import httpx

class Game_manager:
	game_manager_instance = None

	def __init__(self):
		self.update_databases()
		self.private_rooms = {}
		self.username_generator = GenerateUsername()
		self._task = None
		self._is_running_mutex = threading.Lock()
		self._current_games = {}
		self._current_games_mutex = threading.Lock()
		self.status_timer = {
			'waiting': 10,
			'loading' : 60,
			'in_progress': 3600
		}

	def update_databases(self):
		if apps.is_installed('game_manager') and 'game_manager_player' in connection.introspection.table_names():
			players = Player.objects.all()
			#	for player in players:
			#		if player.status != 'inactive':
			#			player.update_status('inactive')
			if players:
				[player.update_status('inactive') for player in players if player.status!= 'inactive']
		if apps.is_installed('game_manager') and 'game_manager_gameinstance' in connection.introspection.table_names():
			games_instance = GameInstance.objects.all()
			if games_instance:
				for game_instance in games_instance:
					if game_instance.status != 'finished'\
						and  game_instance.status != 'aborted':
						game_instance.abort_game()

	def generate_username(self):
		logger.debug("generate new username")
		return self.username_generator.generate()

	def add_private_room(self, username):
		self.private_rooms[username] = PrivateRoom(username)
		return self.private_rooms[username]

	def add_new_game(self, game_id):
		game = GameInstance.get_game(game_id)
		if game.status and game.status != 'finished' and game.status != 'aborted':
			with self._current_games_mutex:
				self._current_games[game_id] = {
					'status': game.status,
					'latest_update_status': Timer(),
					'players': list(GamePlayer.objects.filter(game=game).values_list('player__username', flat=True))
				}

	# game notify

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
	
	# LOOP

	@sync_to_async	
	def _set_current_game_status(self, game_id):
		current_game = self._current_games[game_id]
		game_instance = GameInstance.get_game(game_id)
		if game_instance and game_instance.status \
			and game_instance.status != 'finished' and game_instance.status != 'aborted':
			if current_game['latest_update_status'].get_elapsed_time() >= self.status_timer[current_game['status']]:
				if game_instance.status != self._current_games[game_id]['status']:
					logger.debug(f"{current_game['latest_update_status'].get_elapsed_time()}s elapsed with status : {self._current_games[game_id]['status']}")
					current_game['status'] = game_instance.status
					current_game['latest_update_status'].reset()
					return None, None
				else:
					logger.debug(f"{current_game['latest_update_status'].get_elapsed_time()}s abort game : {self._current_games[game_id]['status']}")
					for player in current_game['players']:
						player_instance = Player.get_or_create_player(player)
						player_instance.update_status('inactive')
					return game_id, game_instance.game_mode
		else:
			return game_id, None

	async def _game_manager_logic(self):
		with self._current_games_mutex:
			for game_id in self._current_games:
				#logger.debug(f"{game_id} check status...")
				result = await self._set_current_game_status(game_id)
				if result:
					game_id, game_mode = result
					if game_mode:
						await self.game_abort_notify(game_id, game_mode)

					if game_id:
						del self._current_games[game_id]
						break



	async def _game_manager_loop(self):
		logger.debug("game_manager loop started")
		while True:
			with self._is_running_mutex:
				if not self._is_running:
					break
			#logger.debug("game_manager loop is running...")
			await self._game_manager_logic()
			await asyncio.sleep(1)

	async def start_game_manager_loop(self):
		with self._is_running_mutex:
			self._is_running = True
		self._task = asyncio.create_task(self._game_manager_loop())
		try:
			await self._task
		except asyncio.CancelledError:
			logger.debug("Game_manager loop has been cancelled.")
		finally:
			logger.debug("Exiting game_manager loop.")

	def stop_game_manager(self):
		logger.debug("Game_manager stopping...")
		with self._is_running_mutex:
			self._is_running = False
			if self._task:
				self._task.cancel()

def create_game_manager_instance():
	if Game_manager.game_manager_instance is None:
		logger.debug("creating game manager...")
		Game_manager.game_manager_instance = Game_manager()
		logger.debug("game manager created !")