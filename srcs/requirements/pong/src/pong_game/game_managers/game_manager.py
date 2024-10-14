from ..game.game import Game
from ..utils.logger import logger
from .data import game_modes
import uuid
import copy

class game_manager:
	def __init__(self) :
		self.games_room = {}
		self.waiting_room = {}
		logger.debug("\ngame_manager initialised\n")

	def add_waiting_room(self, game_id, admin_id, game_mode, players_list):
		if (game_mode not in game_modes):
			logger.debug(f"Error: Wrong game_mode: {game_mode}")
			return None
		if len(players_list) != game_modes[game_mode]['players']:
			logger.debug(f"Error: Wrong nomber of players for the game mode {game_mode}: {len(players_list)}")
			return None
		if game_mode not in self.waiting_room:
			self.waiting_room[game_mode] = {}
		self.waiting_room[game_mode][game_id] = {
			'admin_id': admin_id,
			'expected_players': players_list,
			'players': {},
			'spectator': {},
			'game_instance': None
		}
		return self.waiting_room[game_mode][game_id]

	def add_player(self, username, consumer, game_id):
		room = None
		room_types = [self.waiting_room, self.games_room]
		for room_type in room_types:
			for game_mode in game_modes:
				if game_mode in room_type:
					if game_id not in room_type[game_mode]:
						continue
					room = room_type[game_mode][game_id]
					users = room['players']
					if username not in room['expected_players']:
						users = room['spectator']
					users[username] = consumer
					if len(room['players']) is game_modes[game_mode]['players'] and room_type is self.waiting_room:
						if game_mode not in self.games_room:
							self.games_room[game_mode] = {}
						self.games_room[game_mode][game_id] = room
						del self.waiting_room[game_mode][game_id]
						room = self.games_room[game_mode][game_id]
						new_game = Game(room['players'])
						room['game_instance'] = new_game
					break
		return room

	def remove_player(self, username, game_id):
		room_types = [self.waiting_room, self.games_room]
		for room_type in room_types:
			for game_mode in game_modes:
				if game_mode in room_type:
					if game_id not in room_type[game_mode]:
						continue
					room = room_type[game_mode][game_id]
					users = room['players']
					if username not in room['expected_players']:
						users = room['spectator']
					if username in users:
						del users[username]

	def remove_room(self, game_id):
		room_types = [self.waiting_room, self.games_room]
		for room_type in room_types:
			for game_mode in game_modes:
				if game_mode in room_type:
					if game_id in room_type[game_mode]:
						del room_type[game_mode][game_id]

	def get_room(self, game_id):
		room_types = [self.waiting_room, self.games_room]
		for room_type in room_types:
			for game_mode in game_modes:
				if game_mode in room_type:
					if game_id in room_type[game_mode]:
						return room_type[game_mode][game_id]
		return None


game_manager = game_manager()
