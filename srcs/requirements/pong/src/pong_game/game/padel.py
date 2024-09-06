
class Padel:
	def __init__(self):
		import copy
		from .data import padel_data

		self.position = copy.copy(padel_data['pos'])
		self.direction = 0
		self.speed = padel_data['spd']

	def update_padel_position(self):
		from .data import arena_data
		from .data import padel_data

		padel_destination = self.position['y'] + self.direction * self.speed
		padel_collider = padel_destination + (padel_data['size']['y'] / 2) * self.direction
		border_collider = arena_data['size']['y'] / 2

		if padel_collider <= border_collider and padel_collider >= - border_collider:
			self.position['y'] = padel_destination
		elif self.direction == 1:
			self.position['y'] = border_collider - (padel_data['size']['y'] / 2)
		elif self.direction == -1:
			self.position['y'] = - border_collider + (padel_data['size']['y'] / 2)

	def up(self):
		self.direction = 1

	def down(self):
		self.direction = -1

	def stop(self):
		self.direction = 0

	def stop_up(self):
		if self.direction == 1:
			self.stop()

	def stop_down(self):
		if self.direction == -1:
			self.stop()