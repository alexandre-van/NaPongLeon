from .padel import Padel
from .timer import Timer

class Player:
	def __init__(self, player_consumer, side):
		self.player_consumer = player_consumer
		self.side = side
		self.padel = Padel(self)

	def move_padel(self, input):
		from .data import input_data
		if input == input_data['up']:
			self.padel.up()
		elif input == input_data['down']:
			self.padel.down()
		elif input == input_data['stop_up']:
			self.padel.stop_up()
		elif input == input_data['stop_down']:
			self.padel.stop_down()