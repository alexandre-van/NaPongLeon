from .data import padel_data

class Padel:
	def __init__(self, player):
		import copy
		from .timer import Timer

		self.player = player
		self.position = copy.copy(padel_data['pos'])
		self.position['x'] *= 1 if self.player.side == 'right' else -1
		self.destination = None
		self.direction = 0
		self.ball_contact = None
		self.speed = padel_data['spd']
		self.timer = Timer()

	def border_collision(self, collider):
		from .data import arena_data
		border_collider = arena_data['size']['y'] / 2
		if collider < border_collider and collider > - border_collider:
			return
		elif self.direction == 1:
			self.destination = border_collider - (padel_data['size']['y'] / 2)
		elif self.direction == -1:
			self.destination = - border_collider + (padel_data['size']['y'] / 2)

	def padel_collision(self, collider, ball):
		from .data import ball_data
		ball_collider = ball.position['y'] - ball_data['rad'] * self.direction
		if ball.position['x'] <= self.position['x'] - padel_data['size']['x'] / 2 \
			or self.position['x'] + padel_data['size']['x'] / 2 <= ball.position['x']:
			return
		if self.direction == 1 and collider > ball_collider \
				and self.position['y'] < ball_collider:
			self.destination = ball_collider - (padel_data['size']['y'] / 2)
			if ball.priority == False:
				self.ball_contact = {
					'x': ball.position['x'],
					'y': ball_collider - (padel_data['size']['y'] / 2)
				}
		elif self.direction == -1 and collider < ball_collider \
				and self.position['y'] > ball_collider:
			self.destination = ball_collider + (padel_data['size']['y'] / 2)
			if ball.priority == False:
				self.ball_contact = {
					'x': ball.position['x'],
					'y': ball_collider + (padel_data['size']['y'] / 2)
				}

	def update_padel_position(self, ball):
		if self.ball_contact != None:
			self.ball_contact = None
			return
		self.destination = self.position['y'] + self.direction \
							* self.speed * self.timer.get_elapsed_time()
		self.timer.reset()
		collider = self.position['y'] + (padel_data['size']['y'] / 2) * self.direction
		self.border_collision(collider)
		self.padel_collision(collider, ball)
		self.position['y'] = self.destination
		if ball.priority == True:
			ball.priority = False

	def get_hitbox(self):
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