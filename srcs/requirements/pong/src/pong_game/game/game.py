from .player import Player
from .ball import Ball
from ..utils.logger import logger

class Game:
	def __init__(self, players):
		from .timer import Timer
		import random

		sides = ['left', 'right']
		random.shuffle(sides)  # Mélange aléatoire des côtés
		self.players = {}
		# Assigner les côtés aux joueurs dynamiquement
		for i, (username, player_consumer) in enumerate(players.items()):
			side = sides[i % len(sides)]  # Assigner gauche/droite de manière cyclique
			self.players[username] = Player(player_consumer, side)
			logger.debug(f"{username} is the {side} player !")
		self.ball = Ball()
		self.timer = Timer()
		self.timer.settup(None)
		self.wait = 3

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
			self.ball.update_ball_position(self.get_player_in_side)
		else:
			self.ball.timer.reset()
		return {
			'type': "gu", #game update
			'bp': self.ball.position,
			'pp': {
				'p1': self.get_player_in_side('left').padel.position['y'],
				'p2': self.get_player_in_side('right').padel.position['y']
			}
		}

	def export_data(self):
		from .data import input_data, key_data
		from .data import arena_data, padel_data, ball_data
		return {
			'input': input_data,
			'key': key_data,
			'arena': arena_data,
			'padel': padel_data,
			'ball': ball_data,
			'teams': self.export_teams()
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
	
	def get_player_in_side(self, side):
		for username in self.players:
			if self.players[username].side == side:
				return self.players[username]
		return None
	
	def scored(self, scoring_side):
		self.ball.reset_position()
		player = self.get_player_in_side(scoring_side)
		player.score += 1
		if player.score >= 3:
			return {
				'type': 'game_end',
				'reason': 'The ' + str(scoring_side) + ' side wins !',
				'score': str(player.score),
				'team': str(scoring_side),
			}
		else:
			self.timer.reset()
			self.wait = 1
			return {
				'type': 'scored',
				'msg': 'The ' + str(scoring_side) + ' scores : ' + str(player.score),
				'score': str(player.score),
				'team': str(scoring_side),
			}
		