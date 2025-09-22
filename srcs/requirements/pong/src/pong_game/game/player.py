from .padel import Padel
from .timer import Timer
from .getdata import get_data

class Player:
	def __init__(self, username, player_consumer, side, game_mode, modifiers):
		self.player_consumer = player_consumer
		self.side = side
		self.username = username
		self.padel = Padel(self, game_mode, modifiers)
		self.input_data = get_data(modifiers, 'input_data')

	def move_padel(self, input):
		
		if input == self.input_data['up']:
			self.padel.up()
		elif input == self.input_data['down']:
			self.padel.down()
		elif input == self.input_data['stop_up']:
			self.padel.stop_up()
		elif input == self.input_data['stop_down']:
			self.padel.stop_down()