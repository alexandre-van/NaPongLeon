from .player import Player
from .ball import Ball
from ..utils.logger import logger

class Game:
	def __init__(self, players, game_mode):
		from .timer import Timer
		import random

		sides = ['left', 'right']
		random.shuffle(sides)  # Mélange aléatoire des côtés
		self.game_mode = game_mode
		self.players = {}
		self.players_in_side = {
			'left': [],
			'right': []	
		}
		self.score = {
			'left': 0,
			'right': 0	
		}
		for i, (username, player_consumer) in enumerate(players.items()):
			side = sides[i % len(sides)]
			self.players[username] = Player(player_consumer, side)
			self.players_in_side[side].append(self.players[username])
			logger.debug(f"{username} is the {side} player !")
		self.ball = Ball()
		self.timer = Timer()
		self.timer.settup(None)
		self.wait = 3
		maps = ['mountain', 'island']
		random.shuffle(maps)
		self.map = maps[0]

	def input_players(self, username, input):
		self.players[username].move_padel(input)

	def update(self):
		scoring_side = self.ball.is_scored()
		if scoring_side != None:
			return self.scored(scoring_side)
		for username in self.players:
			self.players[username].padel.update_padel_position(self.ball)
		if (self.timer.waiting(self.wait)):
			self.wait = 0
			self.ball.update_ball_position(self.get_players_in_side)
		else:
			self.ball.timer.reset()
		return {
			'type': "gu", #game update
			'bp': self.ball.position,
			'pp': self.export_padels_position()
		}

	def export_padels_position(self):
		if self.game_mode == 'PONG_CLASSIC':
		# Mode 1v1
			return {
				'p1': self.players_in_side['left'][0].padel.position['y'],
				'p2': self.players_in_side['right'][0].padel.position['y']
			}
		elif self.game_mode == 'PONG_DUO':
			# Mode 2v2
			padels_position = {
				f'p{i + 1}': player.padel.position['y']
				for i, player in enumerate(self.players_in_side['left'])
			}
			padels_position.update({
				f'p{i + 3}': player.padel.position['y']
				for i, player in enumerate(self.players_in_side['right'])
			})
			return padels_position
		else:
			# Gestion d'autres modes de jeu si nécessaire
			return {}

	def export_data(self):
		from .data import input_data, key_data
		from .data import arena_data, padel_data, ball_data
		return {
			'input': input_data,
			'key': key_data,
			'arena': arena_data,
			'padel': padel_data,
			'ball': ball_data,
			'teams': self.export_teams(),
			'map': self.map,
			'game_mode': self.game_mode
		}
	
	def export_teams(self):
		left = []
		right = []
		for player in self.players:
			if self.players[player].side == 'left':
				left.append(player)
			elif self.players[player].side == 'right':
				right.append(player)
		return {
			'left': list(left),
			'right': list(right)
		}

	def getopponent(self, self_username):
		for username in self.players:
			if username != self_username:
				return self.players[username].player_consumer
		return None
	
	def get_players_in_side(self, side):
		if side in self.players_in_side:
			return self.players_in_side[side]
		return None
	
	def scored(self, scoring_side):
		self.ball.reset_position()
		self.score[scoring_side] += 1
		if self.score[scoring_side] >= 3:
			return {
				'type': 'game_end',
				'reason': 'The ' + str(scoring_side) + ' side wins !',
				'score': str(self.score[scoring_side]),
				'team': str(scoring_side),
			}
		else:
			self.timer.reset()
			self.wait = 1
			return {
				'type': 'scored',
				'msg': 'The ' + str(scoring_side) + ' scores : ' + str(self.score[scoring_side]),
				'score': str(self.score[scoring_side]),
				'team': str(scoring_side),
			}
		