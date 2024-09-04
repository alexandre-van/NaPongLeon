import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongGame:
	def __init__(self, player_1, player_2):
		self.players = [player_1, player_2]
		self.ball_position = {'x': 0, 'y': 0}
		self.ball_direction = {'x': 1, 'y': 1}
		self.ball_speed = 5
		self.players_speed = 3
		self.players_position_y = { 'player_1': 0, 'player_2': 0}
		self.players_dir_y = { 'player_1': 0, 'player_2': 0}

	def update_player_position(self, player, input):
		player_key = 'player_1' if player == self.players[0] else 'player_2'
		if input == 'keydown_up':
			self.players_dir_y[player_key] = 1
		elif input == 'keydown_down':
			self.players_dir_y[player_key] = -1
		elif input == 'keyup_up' and self.players_dir_y[player_key] == 1:
			self.players_dir_y[player_key] = 0
		elif input == 'keyup_down' and self.players_dir_y[player_key] == -1:
			self.players_dir_y[player_key] = 0

	def update(self):
		self.ball_position['x'] += self.ball_direction['x'] * self.ball_speed
		self.ball_position['y'] += self.ball_direction['y'] * self.ball_speed
		self.players_position_y['player_1'] += self.players_dir_y['player_1'] * self.players_speed
		self.players_position_y['player_2'] += self.players_dir_y['player_2'] * self.players_speed
		if self.ball_position['x'] >= 30 or self.ball_position['x'] <= -30:
			self.ball_direction['x'] *= -1
		if self.ball_position['y'] >= 40 or self.ball_position['y'] <= -40:
			self.ball_direction['y'] *= -1
		if self.players_position_y['player_1'] >= 30 or self.players_position_y['player_1'] <= -30:
			self.players_dir_y['player_1'] *= 0
		if self.players_position_y['player_2'] >= 30 or self.players_position_y['player_2'] <= -30:
			self.players_dir_y['player_2'] *= 0
		return json.dumps({
			'type' : 'game_update',
			'ball': self.ball_position,
			'players_position_y': self.players_position_y
		})

	def getopponent(self, player):
		return self.players[0] if player == self.players[0] else self.players[1]