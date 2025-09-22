from ..game.game import Game
from ..utils.logger import logger
from .data import game_modes
import uuid
import copy

class game_manager:
	def __init__(self) :
		self.games_room = {}
		self.status_list = [
			'waiting', 'startup', 'loading', 'running', 'aborted', 'finished'
		]
		logger.debug("\ngame_manager initialised\n")

	def add_games_room(self, game_id, admin_id, game_mode, modifiers, players_list, special_id=None, teamlist=None):
		if (game_mode not in game_modes):
			logger.debug(f"Error: Wrong game_mode: {game_mode}")
			return None
		if len(players_list) != game_modes[game_mode]['players']:
			logger.debug(f"Error: Wrong nomber of players for the game mode {game_mode}: {len(players_list)}")
			return None
		self.games_room[game_id] = {
			'status': 'waiting',
			'game_mode': game_mode,
			'modifiers': modifiers,
			'admin': {
				'id': admin_id,
				'consumer': None
			},
			'expected_players': players_list,
			'players': {},
			'spectator': {},
			'teamlist': teamlist,
			'special_id': special_id,
			'game_instance': None
		}
		return self.games_room[game_id]

	def special_connection(self, special_id, game_id):
		if game_id not in self.games_room:
			return None
		room = self.games_room[game_id]
		if not room['special_id']:
			return None
		for ids in room['special_id']:
			private_id = ids.get('private')
			if private_id == special_id:
				public_id = ids.get('public')
				if public_id == 'randomize':
					public_id = str(uuid.uuid4())
				if public_id:
					return public_id
				else:
					return None
		return None

	def add_user(self, username, consumer, game_id):
		if game_id not in self.games_room:
			return None
		room = self.games_room[game_id]
		if not room['admin']['consumer']:
			return None
		users = room['players']
		log_user = 'Player'
		if username not in room['expected_players']:
			users = room['spectator']
			log_user = 'Spectator'
		logger.debug(f"{log_user}: {username} is in waiting room !")
		users[username] = consumer
		logger.debug(f"players: {room['players']}")
		game_mode = room['game_mode']
		modifiers = room['modifiers']
		teamlist = room['teamlist']
		if room['status'] == 'waiting'\
			and len(room['players']) is game_modes[game_mode]['players']:
			logger.debug('player start the game')
			room['status'] = 'startup'
			new_game = Game(room['players'], game_mode, modifiers, teamlist) # add teams list
			room['game_instance'] = new_game
		return room

	def add_admin(self, admin_id, consumer, game_id):
		if game_id not in self.games_room:
			return None
		room = self.games_room[game_id]
		room_admin_id = room['admin']['id']
		if admin_id != room['admin']['id']:
			logger.debug('wrong admin_id')
			logger.debug(f'admin_id : {room_admin_id}')
			return None
		room['admin']['consumer'] = consumer
		game_mode = room['game_mode']
		teamlist = room['teamlist']
		if room['status'] == 'waiting'\
			and len(room['players']) is game_modes[game_mode]['players'] \
			and room['admin']['consumer']:
			logger.debug('admin start the game')
			room['status'] = 'startup'
			new_game = Game(room['players'], teamlist) # add teams list)
      
      
			room['game_instance'] = new_game
		return room

	def update_status(self, status, game_id):
		if game_id not in self.games_room \
			or status not in self.status_list:
			return None
		room = self.games_room[game_id]
		room['status'] = status

	def remove_user(self, username, game_id):
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

	def abortgame(self, game_id):
		if game_id in self.games_room:
			self.games_room[game_id]['status'] = 'aborted'
			return True
		else:
			return None

game_manager = game_manager()
