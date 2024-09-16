
class Ball:
	def __init__(self):
		import copy
		from .timer import Timer
		from .data import ball_data

		self.position = copy.copy(ball_data['pos'])
		self.direction = {'x': 1, 'y': 1}
		self.speed = copy.copy(ball_data['spd'])
		self.timer = Timer()

	def update_ball_position(self, get_player_in_side):
		from .data import arena_data
		from .data import padel_data
		from .data import ball_data
		from .collisions import get_contact_point, get_contact_point_side, get_vector_direction

		destination = self.get_destination()
		destination_collider = self.get_destination_collider(destination)
		for dirX in [1, -1]:
			from ..utils.logger import logger
			padel = get_player_in_side ('right' if dirX == 1 else 'left').padel
			v_dir = get_vector_direction(self.position, destination)
			if destination_collider['x'] * dirX \
					>= padel_data['pos']['x'] - padel_data['size']['x'] / 2 \
				and self.position['x'] * dirX \
					<= padel_data['pos']['x'] - padel_data['size']['x'] / 2 :
				padel_collider = padel.get_collider()
				contact_point = get_contact_point\
					(self.position, ball_data['rad'], v_dir, padel_collider)
				if contact_point != None:
					self.position['x'] = contact_point['x'] - ball_data['rad'] * dirX
					self.position['y'] = contact_point['y']
					self.direction['x'] *= -1
					self.speed['x'] *= 1.05
					return	
			if (self.position['x'] < 0 and self.direction['x'] < 0) \
					or (self.position['x'] > 0 and self.direction['x'] > 0):
				if (destination_collider['y'] >= padel.position['y'] - padel_data['size']['y'] / 2 \
					and self.position['y'] <= padel.position['y'] - padel_data['size']['y'] / 2):
					padel_collider_side = padel.get_collider_side(1)
					contact_point = get_contact_point_side\
						(self.position, ball_data['rad'], v_dir, padel_collider_side)
					if contact_point != None:
						self.position['x'] = contact_point['x']
						self.position['y'] = contact_point['y'] - ball_data['rad']
						self.direction['x'] *= -1
						self.direction['y'] *= -1
						self.speed['x'] *= 1.05
						return
				if destination_collider['y'] <= padel.position['y'] + padel_data['size']['y'] / 2 \
					and self.position['y'] >= padel.position['y'] + padel_data['size']['y'] / 2 :
					padel_collider_side = padel.get_collider_side(-1)
					contact_point = get_contact_point_side\
						(self.position, ball_data['rad'], v_dir, padel_collider_side)
					if contact_point != None:
						self.position['x'] = contact_point['x']
						self.position['y'] = contact_point['y'] + ball_data['rad']
						self.direction['x'] *= -1
						self.direction['y'] *= -1
						self.speed['x'] *= 1.05
						self.speed['y'] = ball_data['spd']['y'] * 2
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
		from .data import ball_data

		return {
			'x': destination['x'] + ball_data['rad'] * self.direction['x'],
			'y': destination['y'] + ball_data['rad'] * self.direction['y']
		}

	def get_border_collider(self):
		from .data import arena_data
		return {
			'x': arena_data['size']['x'] / 2,
			'y': arena_data['size']['y'] / 2
		}
	
	def is_scored(self):
		from .data import ball_data
		border_collider = self.get_border_collider()['x']
		if self.position['x'] + ball_data['rad'] == border_collider:
			return 'left'
		elif self.position['x'] - ball_data['rad'] == -border_collider:	
			return 'right'
		else:
			return None

	def reset_position(self):
		from .data import ball_data
		self.position['x'] = ball_data['pos']['x']
		self.position['y'] = ball_data['pos']['y']
		self.speed['x'] = ball_data['spd']['x']

		#player = get_player_in_side\
		#	('left' if self.position['x'] == border_collider else 'right')
		#player.score += 1
		#if player.score == 5:


