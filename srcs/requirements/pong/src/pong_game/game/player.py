from .padel import Padel

class Player:
	def __init__(self, player_consumer, side):
		self.player_consumer = player_consumer
		self.side = side
		self.padel = Padel()

	def move_padel(self, input):
		from .data import input_data

		getattr(self.padel, input_data[input], None)()