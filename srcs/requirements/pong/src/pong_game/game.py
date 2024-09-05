import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongGame:
	def __init__(self, player_1, player_2):
		self.players = [player_1, player_2]
		self.ball_position = {'x': 0, 'y': 0}
		self.ball_direction = {'x': 1, 'y': 1}
		self.ball_speed = 3
		self.players_speed = 2
		self.players_position = { 'p1': 0, 'p2': 0}
		self.players_direction = { 'p1': 0, 'p2': 0}

	def input_players(self, player, input):
		player_key = 'p1' if player == self.players[0] else 'p2'
		if input == 'keydown_up':
			self.players_direction[player_key] = 1
		elif input == 'keydown_down':
			self.players_direction[player_key] = -1
		elif input == 'keyup_up' and self.players_direction[player_key] == 1:
			self.players_direction[player_key] = 0
		elif input == 'keyup_down' and self.players_direction[player_key] == -1:
			self.players_direction[player_key] = 0

	def update(self):
		ball_pos = self.ball_position
		ball_dir = self.ball_direction
		players_pos = self.players_position
		players_dir = self.players_direction

		ball_pos['x'] += ball_dir['x'] * self.ball_speed
		ball_pos['y'] += ball_dir['y'] * self.ball_speed

		player_dest = players_pos['p1'] + players_dir['p1'] * self.players_speed
		if player_dest <= 30 and player_dest >= -30:
			players_pos['p1'] = player_dest
		else:
			players_pos['p1'] = players_dir['p1'] * 30
		player_dest = players_pos['p2'] + players_dir['p2'] * self.players_speed
		if player_dest <= 30 and player_dest >= -30:
			players_pos['p2'] = player_dest
		else:
			players_pos['p2'] = players_dir['p2'] * 30
		return json.dumps({
			'type' : "game_update",
			'ball_position': self.ball_position,
			'players_position': self.players_position
		})

	def update_players_position(self):

	def getopponent(self, player):
		return self.players[0] if player == self.players[0] else self.players[1]