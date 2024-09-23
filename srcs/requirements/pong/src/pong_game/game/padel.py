
class Padel:
	def __init__(self, player):
		import copy
		from .timer import Timer
		from .data import padel_data

		self.player = player
		self.position = copy.copy(padel_data['pos'])
		self.position['x'] *= 1 if self.player.side == 'right' else -1
		self.direction = 0
		self.speed = padel_data['spd']
		self.timer = Timer()

	def update_padel_position(self):
		from .data import arena_data
		from .data import padel_data

		self.position['y'] = self.position['y'] + self.direction \
							* self.speed * self.timer.get_elapsed_time()
		self.timer.reset()
		collider = self.position['y'] + (padel_data['size']['y'] / 2) * self.direction
		border_collider = arena_data['size']['y'] / 2

		if collider <= border_collider and collider >= - border_collider:
			return
		elif self.direction == 1:
			self.position['y'] = border_collider - (padel_data['size']['y'] / 2)
		elif self.direction == -1:
			self.position['y'] = - border_collider + (padel_data['size']['y'] / 2)

	def get_hitbox(self):
		from .data import padel_data
		return {
			'A': {
				'x': self.position['x'] + padel_data['size']['x'] / 2,
				'y': self.position['y'] + padel_data['size']['y'] / 2
			},
			'B': {
				'x': self.position['x'] + padel_data['size']['x'] / 2,
				'y': self.position['y'] - padel_data['size']['y'] / 2
			},
			'C': {
				'x': self.position['x'] - padel_data['size']['x'] / 2,
				'y': self.position['y'] - padel_data['size']['y'] / 2
			},
			'D': {
				'x': self.position['x'] - padel_data['size']['x'] / 2,
				'y': self.position['y'] + padel_data['size']['y'] / 2
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