from django.conf import settings
from .models import Player, GameInstance, PlayerGameHistory, GamePlayer, GameScore, WinRate, GameMode
from .utils.logger import logger
from admin_manager.admin_manager import AdminManager
from .utils.timer import Timer
from django.apps import apps
from django.db import connection
from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone
import threading
import asyncio
import httpx
import uuid
import copy

class Game_manager:
	game_manager_instance = None

	def __init__(self):
		self.update_databases()
		self._task = None
		self._is_running_mutex = threading.Lock()
		self._current_games = {}
		self._current_games_mutex = threading.Lock()
		self.status_timer = {
			'waiting': 15,
			'loading' : 15,
			'in_progress': 3600,
			'aborting': 15
		}

	def update_databases(self):
		if apps.is_installed('game_manager') and 'game_manager_player' in connection.introspection.table_names():
			players = Player.objects.all()
			if players:
				[player.update_status('inactive') for player in players if player.status!= 'inactive']
		if apps.is_installed('game_manager') and 'game_manager_gameinstance' in connection.introspection.table_names():
			games_instance = GameInstance.objects.all()
			if games_instance:
				for game_instance in games_instance:
					if game_instance.status != 'finished'\
						and  game_instance.status != 'aborted':
						game_instance.abort_game()

	def add_new_game(self, game_id):
		game = GameInstance.get_game(game_id)
		if game.status and game.status not in ['finished', 'aborted']:
			with self._current_games_mutex:
				players_queryset = PlayerGameHistory.objects.filter(game=game)
				logger.debug(f"Raw PlayerGameHistory queryset for game {game_id}: {players_queryset}")
			
				players_list = list(players_queryset.values_list('player__username', flat=True))
				logger.debug(f"Player usernames for game {game_id}: {players_list}")
	
				self._current_games[game_id] = {
					'status': game.status,
					'latest_update_status': Timer(),
					'players': players_list
				}
			
	async def get_game_history(self, username):
		player = await self.fetch_player(username)
		history = await self.fetch_history(player)
		if not history:
			return {}
		game_entries = await self.extract_game_ids(history)
		history_dict = {}
		for game_date, game_id in game_entries:
			game_data = await self.get_game_data(game_id)
			if game_data:
				game_data['self_team'] = ''
				teams = game_data.get('teams')
				if teams:
					for team_name in teams:
						for playername in teams[team_name]:
							logger.debug(f"{playername} == {username}")
							if playername == username:
								game_data['self_team'] = team_name
				date_key = game_date.strftime("%Y-%m-%d %H:%M:%S")
				history_dict[date_key] = game_data
		return history_dict

	async def create_game(self, game_mode, modifiers, players_list, teams_list, ia_authorizes, special_id):
		# pars game_mode
		game_mode_data = settings.GAME_MODES.get(game_mode) 
		if game_mode_data is None:
			return None
		# pars modifiers
		modifiers_list = self.parse_modifier(modifiers, game_mode)
		if modifiers_list is None:
			return None
		# pars players_list
		if len(players_list) > game_mode_data['number_of_players']\
			or (ia_authorizes is False and len(players_list) < game_mode_data['number_of_players']):
			return None
		# pars teams_list
		if teams_list:
			if game_mode_data['team_names'] is None\
				or len(teams_list) != len(game_mode_data['team_names']):
				return None
			else:
				for i, team_name in enumerate(game_mode_data['team_names']):
					if  i >= len(teams_list):
						teams_list.append([])
			number_of_players = 0
			for team in teams_list:
				team_size = len(team)
				if team_size > game_mode_data['team_size']:
					return None
				number_of_players += team_size
			if number_of_players != len(players_list):
				return None
			if all(any(player in team for team in teams_list) for player in players_list) is False:
				return None
		# ai
		all_ai = []
		while ia_authorizes and len(players_list) < game_mode_data['number_of_players']:
			ai_id = {
				'private': str(uuid.uuid4()),
				'public': str(uuid.uuid4()),
				'nickname': 'AI'
			}
			all_ai.append(ai_id)
			special_id.append(ai_id)
			players_list.append(ai_id['public'])
			if teams_list:
				for team in teams_list:
					if len(team) < game_mode_data['team_size']:
						team.append(ai_id['public'])
						break
		logger.debug(f"team_list = {teams_list}")
		game_id = str(uuid.uuid4())
		admin_id = str(uuid.uuid4())
		game = None
		game_connected = await self.connect_to_game(game_id, admin_id, game_mode, modifiers, players_list, teams_list, special_id)
		if game_connected:
			game = await self.create_new_game_instance(game_id, game_mode, modifiers_list, players_list)
			if not game:
				await self.disconnect_to_game(game_id, game_mode)
		else:
			return None
		ai_url = "http://ia:5000/api/ia/create_ia/"
		for ai_id in all_ai:
			try:
				ids = {
					'game_id': game_id,
					'ai_id': ai_id,
				}
				async with httpx.AsyncClient() as client:
					response = await client.post(ai_url, json=ids)

				if response.status_code == 200:
					continue
				else:
					logger.error(f"Failed to create AI {ai_id}: {response.status_code} - {response.text}")
					return None
			except httpx.RequestError as e:
				logger.error(f"AI service error for AI {ai_id}: {str(e)}")
				return None
		return {
			'game_id': game_id,
			'service_name': game_mode_data['service_name']
		}
	
	async def game_notify(self, game_id, admin_id, game_mode, modifiers, players, teams_list, special_id=None):
		game_service_url = settings.GAME_MODES.get(game_mode).get('service_url_new_game')
		send = {'gameId': game_id, 'adminId': admin_id, 'gameMode': game_mode, 'playersList': players, 'teamsList': teams_list, 'special_id': special_id}
		logger.debug(f"send to {game_service_url}: {send}")
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(game_service_url, json={
					'gameId': game_id,
					'adminId': admin_id,
					'gameMode': game_mode,
					'modifiers': modifiers,
					'playersList': players,
					'teamsList': teams_list,
					'special_id': special_id,
				})
			if response and response.status_code == 201 :
				return True
			else:
				logger.debug(f'Error api request Game, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"Game service error: {str(e)}")
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
			logger.error(f"Game service error: {str(e)}")
		return False

	# game connection

	async def connect_to_game(self, game_id, admin_id, game_mode, modifiers, players, teams_list=None, special_id=None):
		is_game_notified = await Game_manager.game_manager_instance.game_notify(
			game_id, admin_id, game_mode, modifiers, players, teams_list, special_id)
		if is_game_notified:
			logger.debug(f'Game service {game_id} created with players: {players}')
			AdminManager.admin_manager_instance.start_connections(game_id, admin_id, game_mode)
			return True
		else:
			return False

	async def disconnect_to_game(self, game_id, game_mode):
		is_game_notified = await Game_manager.game_manager_instance.game_abort_notify(game_id, game_mode)
		if is_game_notified:
			logger.debug(f'Game service {game_id} aborted')
			return True
		else:
			logger.debug(f'Game serice {game_id} was not aborted')
			return False

	# LOOP

	@sync_to_async	
	def _set_current_game_status(self, game_id):
		current_game = self._current_games[game_id]
		game_instance = GameInstance.get_game(game_id)
		if game_instance and game_instance.status\
			and game_instance.status != 'finished' and game_instance.status != 'aborted':
			if current_game['latest_update_status'].get_elapsed_time() \
				>= self.status_timer[current_game['status']]:
					if game_instance.status != self._current_games[game_id]['status']:
						logger.debug(f"{current_game['latest_update_status'].get_elapsed_time()}s elapsed with status : {self._current_games[game_id]['status']}")
						current_game['status'] = game_instance.status
						current_game['latest_update_status'].reset()
						return None, None
					#elif self.game_instance.status != 'aborting':
					#	logger.debug(f"{current_game['latest_update_status'].get_elapsed_time()}s aborting game... : {self._current_games[game_id]['status']}")
					#	game_instance.aborting_game()
					#	current_game['status'] = game_instance.status
					#	current_game['latest_update_status'].reset()
					#	return None, None
					else:
						logger.debug(f"{current_game['latest_update_status'].get_elapsed_time()}s abort game : {self._current_games[game_id]['status']}")
						for player in current_game['players']:
							player_instance = Player.get_player(player)
							if player_instance:
								player_instance.update_status('inactive')
						game_instance.abort_game()
						return game_id, game_instance.game_mode
			else :
				return None, None
		else:
			for player in current_game['players']:
				player_instance = Player.get_player(player)
				if player_instance:
					player_instance.update_status('inactive')
			return game_id, None

	async def _game_manager_logic(self):
		with self._current_games_mutex:
			for game_id in self._current_games:
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

	async def get_user_status(self, username):
		status = await self.get_player_status(username)
		if status:
			ret = {'status': status}
			if status in ['pending', 'waiting', 'loading', 'in_game']:
				player_history = await self.fetch_history(await self.fetch_player(username))
				game_id = await self.get_last_game_id(player_history)
				if game_id:
					game_data = await self.get_game_data(game_id)
					ret['game_mode'] = game_data['game_mode']
					ret['game_id'] = game_data['game_id']
					game_mode_data = settings.GAME_MODES.get(ret['game_mode'])
					ret['game_service'] = game_mode_data['service_name']
			return ret
		else:
			return None
		
	async def get_user_win_rate(self, username, game_mode):
		data = await self.get_win_rate(username, game_mode)
		if data:
			return data

	# db

	@sync_to_async
	def get_last_game_id(self, player_history):
		if player_history:
			latest_game = player_history[-1]
			return latest_game.game.game_id
		return None

	async def create_new_game_instance(self, game_id, game_mode, modifiers, players):
		game = await self.create_game_instance(game_id, game_mode, modifiers, players)
		if game:
			for username in players:
				await self.update_player_status(username, 'pending')
			return game
		else:
			return None
		
	async def create_new_player_instance(self, username):
		await self.create_player_instance(username)

	@sync_to_async
	def get_game_instance(self, game_id):
		return GameInstance.get_game(game_id)

	@sync_to_async
	def create_game_instance(self, game_id, game_mode, modifiers, players):
		with transaction.atomic():
			game_instance = GameInstance.create_game(game_id, game_mode, modifiers, players)
			Game_manager.game_manager_instance.add_new_game(game_id)
			return game_instance
		return None

	@sync_to_async
	def get_player_status(self, username):
		with transaction.atomic():
			player = Player.get_player(username)
			if player:
				return player.status
		return None

	@sync_to_async
	def update_player_status(self, username, status):
		with transaction.atomic():
			player = Player.get_player(username)
			if player:
				player.update_status(status)

	@sync_to_async
	def abord_game_instance(self, game):
		with transaction.atomic():
			game.abort_game()

	@sync_to_async
	def create_player_instance(self, username):
		with transaction.atomic():
			Player.get_or_create_player(username)

	@sync_to_async
	def get_win_rate(self, username, game_mode):
		win_rate = None
		with transaction.atomic():
			player_instance = Player.get_or_create_player(username)
			game_mode_instance = GameMode.get_or_create(game_mode)
			win_rate = WinRate.get_win_rate_data(player_instance, game_mode_instance)
		return win_rate
	
	@sync_to_async
	def get_or_create_win_rate(self, username, game_mode):
		win_rate = None
		with transaction.atomic():
			player_instance = Player.get_or_create_player(username)
			game_mode_instance = GameMode.get_or_create(game_mode)
			win_rate = WinRate.get_or_create_win_rate(player_instance, game_mode_instance)
		return win_rate

	@sync_to_async
	def fetch_player(self, username):
		return Player.objects.get(username=username)

	@sync_to_async
	def fetch_history(self, player):
		history = list(PlayerGameHistory.objects.filter(player=player).order_by('game_date'))
		if not history:
			logger.warning(f"No history found for player {player.username}.")
			return []
		return history

	
	@sync_to_async
	def extract_game_ids(self, history):
		return [
			(timezone.localtime(entry.game_date), entry.game.game_id) 
			for entry in history
		]

	@sync_to_async
	def get_game_data(self, game_id):
		try:
			game_instance = GameInstance.get_game(game_id)
			if not game_instance:
				return None
			game_players = GamePlayer.objects.filter(game=game_instance)
			teams_distribution = {}
			for player_entry in game_players:
				if player_entry.team.name not in teams_distribution:
					teams_distribution[player_entry.team.name] = []
				username = player_entry.player.username
				#nickname = player_entry.player.nickname
				teams_distribution[player_entry.team.name].append(player_entry.player.username)
			game_scores = GameScore.objects.filter(game=game_instance)
			teams_scores = {score.team.name: score.score for score in game_scores}
			game_data = {
				"game_id": game_instance.game_id,
				"status": game_instance.status,
				"winner": game_instance.winner.name if game_instance.winner else None,
				"game_mode": game_instance.game_mode.name,
				"game_date": game_instance.game_date.isoformat(),
				"teams": teams_distribution,
				"scores": teams_scores,
			}
			logger.debug(f"game_data = {game_data}")
			return game_data
		except Exception as e:
			logger.error(f"Error fetching game data: {e}")
			return None
	
	@sync_to_async
	def copy_data(self, data):
		return copy.deepcopy(data)

	#utils

	def parse_modifier(self, modifiers, game_mode):
		modifiers_list = modifiers.split(",") if modifiers else []
		modifiers_list = self.check_modifier(modifiers_list, game_mode)
		return modifiers_list

	def check_modifier(self, modifiers_list, game_mode):
		valid_modifiers = settings.GAME_MODES.get(game_mode).get("modifier_list")
		if modifiers_list:
			if not all(mod in valid_modifiers for mod in modifiers_list):
				return None
			modifiers_list.sort()
		return modifiers_list

def create_game_manager_instance():
	if Game_manager.game_manager_instance is None:
		logger.debug("creating game manager...")
		Game_manager.game_manager_instance = Game_manager()
		logger.debug("game manager created !")