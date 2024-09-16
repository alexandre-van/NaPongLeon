
class Padel:
	def __init__(self, player):
		import copy
		from .timer import Timer
		from .data import padel_data

		self.player = player
		self.position = copy.copy(padel_data['pos'])
		self.direction = 0
		self.speed = padel_data['spd']
		self.position['x'] *= 1 if self.player.side == 'right' else -1
		self.timer = Timer()

	def update_padel_position(self):
		from .data import arena_data
		from .data import padel_data

		destination = self.position['y'] + self.direction \
			* self.speed * self.timer.get_elapsed_time()
		self.timer.reset()
		collider = destination + (padel_data['size']['y'] / 2) * self.direction
		border_collider = arena_data['size']['y'] / 2

		if collider <= border_collider and collider >= - border_collider:
			self.position['y'] = destination
		elif self.direction == 1:
			self.position['y'] = border_collider - (padel_data['size']['y'] / 2)
		elif self.direction == -1:
			self.position['y'] = - border_collider + (padel_data['size']['y'] / 2)

	def get_collider(self):
		from .data import padel_data
		dir = 1 if self.player.side == 'left' else -1
		return {
			'x': self.position['x'] + padel_data['size']['x'] / 2 * dir,
			'y': {
				'top': self.position['y'] + padel_data['size']['y'] / 2,
				'bottom': self.position['y'] - padel_data['size']['y'] / 2
			}
		}
	
	def get_collider_side(self, dirY):
		from .data import padel_data
		return {
			'x': {
				'right': self.position['x'] + padel_data['size']['x'] / 2,
				'left' : self.position['x'] - padel_data['size']['x'] / 2
			},
			'y': self.position['y'] - padel_data['size']['y'] / 2 * dirY
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