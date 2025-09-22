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
		self.threads = {}
		self._threads_mutex = threading.Lock()

	def connect_to_game(self, game_id, ws_url):
		logger.debug(f'new thread created to {ws_url} !')
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		try:
			loop.run_until_complete(self._handle_websocket(game_id, ws_url))
		finally:
			self.cleanup_thread(game_id)

	def cleanup_thread(self, game_id):
		with self._threads_mutex:
			thread_data = self.threads.get(game_id)
			if not thread_data:
				logger.error(f"Thread data for game {game_id} not found. Skipping cleanup.")
				return
	
			users = thread_data.get('users', {})
			logger.debug(f"Cleanup after game {game_id}. Closing resources...")
			logger.debug(f"Users change status: {users}")
			self.update_game_status(game_id, users, 'aborted')
			del self.threads[game_id]
	
		logger.debug(f"Thread for game {game_id} cleaned up.")

	
	async def _handle_websocket(self, game_id, ws_url):
		users = None
		with self._threads_mutex:
			if self.threads.get(game_id):
				users = self.threads[game_id]['users']
				logger.info(f"users : {users}")
		logger.debug(f'thread in game : {game_id} is running...')
		try :
			async with websockets.connect(ws_url) as websocket:
				logger.debug(f"Websocket connected : {ws_url}")
				try:
					async for message in websocket:
						if await self.game_is_aborted(game_id):
							await websocket.close()
						if message:
							message_dict = json.loads(message)
							if message_dict:
								await self.handle_message(game_id, message_dict, users)
				except websockets.exceptions.ConnectionClosedOK:
					logger.debug("WebSocket connection closed normally (1000 OK).")
				except websockets.exceptions.ConnectionClosedError as e:
					logger.error(f"WebSocket closed with error: {e}")
				except json.JSONDecodeError as e:
					logger.error(f"Failed to decode message: {e}")
		except Exception as e:
			logger.error(f"Unexpected error in WebSocket handler for game {game_id}: {e}")

	@sync_to_async
	def game_is_aborted(self, game_id):
		game_instance = GameInstance.get_game(game_id)
		if not game_instance:
			logger.debug("game instance is None")
			return True
		status = game_instance.status
		if status == 'finished' or status == 'aborted':
			return True
		return False

	@sync_to_async
	def handle_message(self, game_id, message, users):
		logger.debug(f"Game {game_id}: Received message: {message}")
		type = message.get("type")
		if type == "export_status":
			status = message.get("status")
			if status == "finished" or status == "aborted":
				win_team = message.get("team")
				score = message.get("score")
				self.set_winner(game_id, win_team, score)
			self.update_game_status(game_id, users, status)
		elif type == "export_teams":
			teams = message.get("teams")
			self.export_teams(game_id, teams)
		elif type == "update_score":
			team = message.get("team")
			score = message.get("score")
			self.update_score(game_id, team, score)
		elif type == "player_connection":
			username = message.get("username")
			if users:
				players = users.get('players')
				players.append(username)
				self.update_user_status(username, 'waiting_for_players')
		elif type == "spectator_connection":
			username = message.get("username")
			if users:
				spectators = users.get('spectators')
				spectators.append(username)
			self.update_user_status(username, 'spectate')
		elif type == "player_disconnection":
			username = message.get("username")
			self.update_user_status(username, 'inactive')
			if users:
				players = users.get('players')
				players.remove(username)
		elif type == "spectator_disconnection":
			username = message.get("username")
			self.update_user_status(username, 'inactive')
			if users:
				spectators = users.get('spectators')
				spectators.remove(username)

	def set_winner(self, game_id, win_team, score):
		game_instance = GameInstance.get_game(game_id)
		if not game_instance:
			logger.debug("game instance is None")
			return
		with transaction.atomic():
			if score:
				game_instance.update_score(win_team, score)
			if win_team:
				game_instance.set_winner(win_team)

	def update_game_status(self, game_id, users, status):
		self.update_users_status_with_game_status(users, status)
		game_instance = GameInstance.get_game(game_id)
		if not game_instance:
			logger.debug("game instance is None")
			return
		if game_instance.status == 'finished' \
			or game_instance.status == 'aborted':
			return
		with transaction.atomic():
			game_instance.update_status(status)

	def update_users_status_with_game_status(self, users, game_status):
		if game_status == 'loading':
			logger.info("change to loading")
			self.change_all_players_status(users, 'loading_game')
		if game_status == 'in_progress':
			logger.info("change to in_progress")
			self.change_all_players_status(users, 'in_game')
		if game_status == 'aborted' or game_status == 'finished':
			logger.info("change to finished")
			self.change_all_players_status(users, 'inactive')
			self.change_all_spectators_status(users, 'inactive')

	def export_teams(self, game_id, teams):
		game_instance = GameInstance.get_game(game_id)
		if not game_instance:
			return
		with transaction.atomic():
			for team in teams:
				for player in teams[team]:
					logger.debug(f"{player}")
					game_instance.add_player_to_team(player, team)
				self.update_score(game_id, team, 0)

	def update_score(self, game_id, team, score):
		game_instance = GameInstance.get_game(game_id)
		if not game_instance:
			return
		with transaction.atomic():
			game_instance.update_score(team, score)

	def change_all_players_status(self, users, status):
		logger.info(f"players : {users['players']}")
		for username in users['players']:
			logger.info(f"{username} status : {status}")
			self.update_user_status(username, status)
		if status == 'inactive':
			for username in users['players']:
				users['players'].remove(username)
		
	def change_all_spectators_status(self, users, status):
		for username in users['spectators']:
			self.update_user_status(username, status)
		if status == 'inactive':
			for username in users['spectators']:
				users['spectators'].remove(username)

	def update_user_status(self, username, status):
		with transaction.atomic():
			player = Player.get_player(username)
			if player:
				player.update_status(status)		

	# ADMIN_MANAGER

	def start_connections(self, game_id, admin_id, game_mode):
		ws_url = settings.GAME_MODES.get(game_mode).get('service_ws') + game_id + '/' + admin_id + '/'
		logger.debug(f'start_new_connection ws - game_id = {game_id}, admin_id = {admin_id}, ws_url = {ws_url}')
		thread = threading.Thread(target=self.connect_to_game, args=(game_id, ws_url))
		thread.start()

		with self._threads_mutex:
			self.threads[game_id] = {
				'thread': thread,
				'users': {
					'players': [],
					'spectators': []
				}
			}

	def force_close(self, game_id):
		with self._threads_mutex:
			if self.threads[game_id]:
				self.threads[game_id]['thread'].stop()

	def close_all(self):
		with self._threads_mutex:
			for game_id in self.threads:
				self.threads[game_id]['thread'].join()
		logger.debug("All threads are closed.")

if AdminManager.admin_manager_instance is None:
	AdminManager.admin_manager_instance = AdminManager()
