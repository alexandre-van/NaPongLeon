from .player import Player
from .ball import Ball

class Game:
	def __init__(self, player_1, player_2):
		import random

		side1, side2 = ('left', 'right') if random.randint(1, 2) == 1 else ('right', 'left')
		self.players = { 
			'p1': Player(player_1, side1),
			'p2': Player(player_2, side2)
		}
		self.ball = Ball()

	def input_players(self, player, input):
		pn = 'p1' if player == self.players['p1'].player_consumer else 'p2'
		self.players[pn].move_padel(input)

	def update(self):
		scoring_side = self.ball.is_scored()
		if scoring_side != None:
			return self.scored(scoring_side)
		self.players['p1'].padel.update_padel_position()
		self.players['p2'].padel.update_padel_position()
		self.ball.update_ball_position(self.get_player_in_side)
		return {
			'type' : "gu", #game update
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
			'ball': ball_data
		}

	def getopponent(self, player):
		return self.players['p1'].player_consumer \
			if player == self.players['p1'].player_consumer \
			else self.players['p2'].player_consumer
	
	def get_player_in_side(self, side):
		return self.players['p1'] if self.players['p1'].side == side \
			else self.players['p2']
	
	def scored(self, scoring_side):
		self.ball.reset_position()
		player = self.get_player_in_side(scoring_side)
		player.score += 1
		if player.score >= 11:
			return {
				'type': 'game_end',
				'reason': 'The ' + str(scoring_side) + ' side wins !'
			}
		else:
			return {
				'type': 'scored',
				'msg': 'The ' + str(scoring_side) + ' scores : ' + str(player.score)
			}