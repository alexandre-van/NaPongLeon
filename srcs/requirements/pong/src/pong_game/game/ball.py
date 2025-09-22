from .getdata import get_data
from .collisions import get_position_physic
from ..utils.logger import logger

class Ball:
	def __init__(self, modifiers):
		from .timer import Timer
		import copy

		self.ball_data = get_data(modifiers,'ball_data')
		self.arena_data = get_data(modifiers,'arena_data')
		self.position = copy.copy(self.ball_data['pos'])
		self.direction = {'x': 1, 'y': self.random_dir()}
		self.speed = copy.copy(self.ball_data['spd'])
		self.random_y_speed()
		self.timer = Timer()
		self.priority = False

	def update_ball_position(self, get_players_in_side):
		destination = self.get_destination()
		# logger.debug(f"dest = {destination}")
		destination_collider = self.get_destination_collider(destination)
		players_in_side = get_players_in_side('right' if destination['x'] > 0 else 'left')
		for player_in_side in players_in_side:
			padel = player_in_side.padel
			if padel.ball_contact:
				self.updateSpeedAndDir(padel, padel.ball_contact, \
					'DA' if padel.direction == 1 else 'BC')
				return 'padel_contact'
			padel_hitbox = padel.get_hitbox()
			physic_position = get_position_physic(self.position, destination, self.ball_data['rad'],\
						padel_hitbox)
			# logger.debug(f"physic_position:{physic_position}")
			if physic_position:
				self.padel_contact(physic_position, padel)
				self.priority = True
				return 'padel_contact'
		border_collider = self.get_border_collider()
		for axis in ['x', 'y']:
			if destination_collider[axis] <= border_collider[axis] \
					and destination_collider[axis] >= -border_collider[axis]:
				self.position[axis] = destination[axis]
			else:
				self.position[axis] \
					= self.direction[axis] * self.arena_data['size'][axis] / 2 \
					- self.direction[axis] * self.ball_data['rad']
				self.direction[axis] *= -1
		return 'gu'
		
	def get_destination(self):
		normalized_speed = self.normalize_speed()
		# logger.debug(f"speed:{self.speed}")
		destination = {
			'x': self.position['x'] + self.direction['x'] \
				* normalized_speed['x'] * self.timer.get_elapsed_time(),
			'y': self.position['y'] + self.direction['y'] \
				* normalized_speed['y'] * self.timer.get_elapsed_time()
		}
		self.timer.reset()
		return destination
		
	def get_destination_collider(self, destination):
		return {
			'x': destination['x'] + self.ball_data['rad'] * self.direction['x'],
			'y': destination['y'] + self.ball_data['rad'] * self.direction['y']
		}

	def get_border_collider(self):
		return {
			'x': self.arena_data['size']['x'] / 2,
			'y': self.arena_data['size']['y'] / 2
		}
	
	def is_scored(self):
		border_collider = self.get_border_collider()['x']
		if self.position['x'] + self.ball_data['rad'] == border_collider:
			return 'left'
		elif self.position['x'] - self.ball_data['rad'] == -border_collider:	
			return 'right'
		else:
			return None

	def reset_position(self):
		import copy
		self.position = copy.copy(self.ball_data['pos'])
		self.direction['y'] = self.random_dir()
		self.speed = copy.copy(self.ball_data['spd'])
		self.random_y_speed()

	def incrased_y_speed(self, incrase):
		if (self.speed['y'] > self.ball_data['spd']['y'] + incrase * 2):
			return
		self.speed['y'] += incrase
		if (self.speed['y'] > self.ball_data['spd']['y'] + incrase * 2):
			self.speed['y'] = self.ball_data['spd']['y'] + incrase * 2

	def decrased_y_speed(self, decrase):
		if (self.speed['y'] < self.ball_data['spd']['y'] - decrase):
			return
		self.speed['y'] -= decrase
		if (self.speed['y'] < self.ball_data['spd']['y'] - decrase):
			self.speed['y'] = self.ball_data['spd']['y'] - decrase


	def updateSpeedAndDir(self, padel, point_contact, segment):
		if segment == 'AB' or segment == 'CD':
			logger.debug("switch")
			self.direction['x'] *= -1
			self.speed['x'] += self.ball_data['spd']['x'] / 6
			if self.speed['x'] >= 2500:
				self.speed['x'] = 2500
			if padel.direction == 0:
				if self.speed['y'] > self.ball_data['spd']['y']:
					self.decrased_y_speed(self.ball_data['spd']['y'] / 4)
				elif self.speed['y'] < self.ball_data['spd']['y']:
					self.incrased_y_speed(self.ball_data['spd']['y'] / 4)
			elif padel.direction != self.direction['y']:
				self.decrased_y_speed(self.ball_data['spd']['y'] / 2)
			elif self.speed['y'] < self.ball_data['spd']['y'] * 2:
				self.incrased_y_speed(self.ball_data['spd']['y'] / 2)
		elif segment == 'BC' or segment == 'DA':
			if (padel.position['x'] < 0 and padel.position['x'] <= point_contact['x']) \
				or (padel.position['x'] > 0 and padel.position['x'] >= point_contact['x']):
				self.direction['x'] *= -1
			self.direction['y'] = 1 if segment == 'DA' else -1
			self.speed['x'] += self.ball_data['spd']['x'] / 6
			if self.speed['x'] >= 2500:
				self.speed['x'] = 2500
			if self.speed['y'] < self.ball_data['spd']['y']:
				self.speed['y'] = self.ball_data['spd']['y']
			if padel.direction == 0:
				self.incrased_y_speed(self.ball_data['spd']['y'] * 0.75)
			elif padel.direction != self.direction['y']:
				self.incrased_y_speed(self.ball_data['spd']['y'])
			else:
				self.incrased_y_speed(self.ball_data['spd']['y'] / 2)

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

	def random_y_speed(self):
		import random
		self.speed['y'] *= random.choice([0.5, 0.75, 1, 1.25, 1.5])

	def normalize_speed(self):
		s_resul = ((self.speed['x']**2 + self.speed['y']**2)**0.5)
		if s_resul != 0:
			factorx = self.speed['x'] / s_resul
			factory = self.speed['y'] / s_resul
			return {
				'x': self.speed['x'] * factorx,
				'y': self.speed['y'] * factory
			}
		else:
			return {
				'x': self.speed['x'],
				'y': self.speed['y']
			}	