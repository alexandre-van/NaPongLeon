
class Padel:
	def __init__(self, player):
		import copy
		from .timer import Timer
		from .data import padel_data

		self.player = player
		self.position = copy.copy(padel_data['pos'])
		self.position['x'] *= 1 if self.player.side == 'right' else -1
		self.destination = copy.copy(self.position)
		self.direction = 0
		self.speed = padel_data['spd']
		self.timer = Timer()

	def update_padel_position(self):
		self.position = self.destination

	def update_padel_desination(self):
		from .data import arena_data
		from .data import padel_data

		self.destination['y'] = self.position['y'] + self.direction \
							* self.speed * self.timer.get_elapsed_time()
		self.timer.reset()
		collider = self.destination['y'] + (padel_data['size']['y'] / 2) * self.direction
		border_collider = arena_data['size']['y'] / 2

		if collider <= border_collider and collider >= - border_collider:
			return
		elif self.direction == 1:
			self.destination['y'] = border_collider - (padel_data['size']['y'] / 2)
		elif self.direction == -1:
			self.destination['y'] = - border_collider + (padel_data['size']['y'] / 2)

	def get_hitbox(self, position):
		from .data import padel_data
		return {
			'A': {
				'x': position['x'] + padel_data['size']['x'] / 2,
				'y': position['y'] + padel_data['size']['y'] / 2
			},
			'B': {
				'x': position['x'] + padel_data['size']['x'] / 2,
				'y': position['y'] - padel_data['size']['y'] / 2
			},
			'C': {
				'x': position['x'] - padel_data['size']['x'] / 2,
				'y': position['y'] - padel_data['size']['y'] / 2
			},
			'D': {
				'x': position['x'] - padel_data['size']['x'] / 2,
				'y': position['y'] + padel_data['size']['y'] / 2
			}
		}

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