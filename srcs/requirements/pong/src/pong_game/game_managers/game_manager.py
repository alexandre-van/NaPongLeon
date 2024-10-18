from ..game.game import Game
from ..utils.logger import logger
from .data import game_modes
import uuid
import copy

class game_manager:
	def __init__(self) :
		self.games_room = {}
		logger.debug("\ngame_manager initialised\n")

	def add_games_room(self, game_id, admin_id, game_mode, players_list):
		if (game_mode not in game_modes):
			logger.debug(f"Error: Wrong game_mode: {game_mode}")
			return None
		if len(players_list) != game_modes[game_mode]['players']:
			logger.debug(f"Error: Wrong nomber of players for the game mode {game_mode}: {len(players_list)}")
			return None
		self.games_room[game_id] = {
			'status': 'waiting',
			'game_mode': game_mode,
			'admin_id': admin_id,
			'expected_players': players_list,
			'players': {},
			'spectator': {},
			'game_instance': None
		}
		return self.games_room[game_id]

	def add_player(self, username, consumer, game_id):
		if game_id not in self.games_room:
			return None
		room = self.games_room[game_id]
		users = room['players']
		if username not in room['expected_players']:
			users = room['spectator']
		users[username] = consumer
		game_mode = room['game_mode']
		if len(room['players']) is game_modes[game_mode]['players'] \
			and room['status'] is 'waiting':
			room['status'] = 'running'
			new_game = Game(room['players'])
			room['game_instance'] = new_game
		return room

	def remove_player(self, username, game_id):
		if game_id not in self.games_room:
			return
		room = self.games_room[game_id]
		users = room['players']
		if username not in room['expected_players']:
			users = room['spectator']
		if username in users:
			del users[username]

	def remove_room(self, game_id):
		if game_id in self.games_room:
			del self.games_room[game_id]

	def get_room(self, game_id):
		if game_id in self.games_room:
			return self.games_room[game_id]
		return None


game_manager = game_manager()
