from .data import ball_data
from .data import arena_data
from .data import padel_data
from .collisions import get_position_physic
from ..utils.logger import logger

class Ball:
	def __init__(self):
		import copy
		from .timer import Timer

		self.position = copy.copy(ball_data['pos'])
		self.direction = {'x': 1, 'y': self.random_dir()}
		self.speed = copy.copy(ball_data['spd'])
		self.timer = Timer()
		self.priority = False

	def update_ball_position(self, get_player_in_side):
		destination = self.get_destination()
		destination_collider = self.get_destination_collider(destination)
		padel = get_player_in_side('right' if destination['x'] > 0 else 'left').padel
		if padel.ball_contact != None:
			self.updateSpeedAndDir(padel, padel.ball_contact, \
				'DA' if padel.direction == 1 else 'BC')
			return
		padel_hitbox = padel.get_hitbox()
		physic_position = get_position_physic(self.position, destination, ball_data['rad'],\
					padel_hitbox)
		if physic_position != None:
			self.padel_contact(physic_position, padel)
			self.priority = True
			return
		border_collider = self.get_border_collider()
		for axis in ['x', 'y']:
			if destination_collider[axis] <= border_collider[axis] \
					and destination_collider[axis] >= -border_collider[axis]:
				self.position[axis] = destination[axis]
			else:
				self.position[axis] \
					= self.direction[axis] * arena_data['size'][axis] / 2 \
					- self.direction[axis] * ball_data['rad']
				self.direction[axis] *= -1
		
	def get_destination(self):
		destination = {
			'x': self.position['x'] + self.direction['x'] \
				* self.speed['x'] * self.timer.get_elapsed_time(),
			'y': self.position['y'] + self.direction['y'] \
				* self.speed['y'] * self.timer.get_elapsed_time()
		}
		self.timer.reset()
		return destination
		
	def get_destination_collider(self, destination):
		return {
			'x': destination['x'] + ball_data['rad'] * self.direction['x'],
			'y': destination['y'] + ball_data['rad'] * self.direction['y']
		}

	def get_border_collider(self):
		return {
			'x': arena_data['size']['x'] / 2,
			'y': arena_data['size']['y'] / 2
		}
	
	def is_scored(self):
		border_collider = self.get_border_collider()['x']
		if self.position['x'] + ball_data['rad'] == border_collider:
			return 'left'
		elif self.position['x'] - ball_data['rad'] == -border_collider:	
			return 'right'
		else:
			return None

	def reset_position(self):
		import random
		import copy
		self.position = copy.copy(ball_data['pos'])
		self.direction['y'] = self.random_dir()
		self.speed = copy.copy(ball_data['spd'])

	def incrased_y_speed(self, incrase):
		if (self.speed['y'] > ball_data['spd']['y'] + incrase * 2):
			return
		self.speed['y'] += incrase
		if (self.speed['y'] > ball_data['spd']['y'] + incrase * 2):
			self.speed['y'] = ball_data['spd']['y'] + incrase * 2

	def decrased_y_speed(self, decrase):
		if (self.speed['y'] < ball_data['spd']['y'] - decrase):
			return
		self.speed['y'] -= decrase
		if (self.speed['y'] < ball_data['spd']['y'] - decrase):
			self.speed['y'] = ball_data['spd']['y'] - decrase


	def updateSpeedAndDir(self, padel, point_contact, segment):
		if segment == 'AB' or segment == 'CD':
			self.direction['x'] *= -1
			self.speed['x'] *= 1.05
			if padel.direction == 0:
				if self.speed['y'] > ball_data['spd']['y']:
					self.decrased_y_speed(ball_data['spd']['y'] / 4)
				elif self.speed['y'] < ball_data['spd']['y']:
					self.incrased_y_speed(ball_data['spd']['y'] / 4)
			elif padel.direction != self.direction['y']:
				self.decrased_y_speed(ball_data['spd']['y'] / 2)
			elif self.speed['y'] < ball_data['spd']['y'] * 2:
				self.incrased_y_speed(ball_data['spd']['y'] / 2)
		elif segment == 'BC' or segment == 'DA':
			if (padel.position['x'] < 0 and padel.position['x'] <= point_contact['x']) \
				or (padel.position['x'] > 0 and padel.position['x'] >= point_contact['x']):
				self.direction['x'] *= -1
			self.direction['y'] = 1 if segment == 'DA' else -1
			self.speed['x'] *= 1.025
			if self.speed['y'] < ball_data['spd']['y']:
				self.speed['y'] = ball_data['spd']['y']
			if padel.direction == 0:
				self.incrased_y_speed(ball_data['spd']['y'] * 0.75)
			elif padel.direction != self.direction['y']:
				self.incrased_y_speed(ball_data['spd']['y'])
			else:
				self.incrased_y_speed(ball_data['spd']['y'] / 2)

	def padel_contact(self, physic_position, padel):
		center_at_contact = physic_position['center_at_contact']
		point_contact = physic_position['point_contact']
		segment = physic_position['segment']
		self.position['x'] = center_at_contact['x']
		self.position['y'] = center_at_contact['y']
		self.updateSpeedAndDir(padel, point_contact, segment)

	def random_dir(self):
		import random
		return 1 if random.randint(1, 2) == 1 else -1