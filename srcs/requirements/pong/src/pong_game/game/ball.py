
class Ball:
	def __init__(self):
		import copy
		from .data import ball_data

		self.position = copy.copy(ball_data['pos'])
		self.direction = {'x': 1, 'y': 1}
		self.speed = ball_data['spd']

	def update_ball_position(self, get_player_in_side):
		from .data import arena_data
		from .data import padel_data
		from .data import ball_data
		from .collisions import check_collisions

		ball_destination = {
			'x': self.position['x'] + self.direction['x'] * self.speed,
			'y': self.position['y'] + self.direction['y'] * self.speed
		}
		ball_collider = {
			'x': ball_destination['x'] + ball_data['rad'] * self.direction['x'],
			'y': ball_destination['y'] + ball_data['rad'] * self.direction['y']
		}
		border_collider = {
			'x': arena_data['size']['x'] / 2,
			'y': arena_data['size']['y'] / 2
		}
		if ball_destination['x'] < - padel_data['pos']['x']:
			player = get_player_in_side('left')
			from ..utils.logger import logger
			logger.log("all point :",\
				self.position['x'], self.position['y'], \
				ball_collider['x'], ball_collider['y'],
				player.padel.position['y'] + padel_data['size']['y'] / 2, - padel_data['pos']['x'],
				player.padel.position['y'] - padel_data['size']['y'] / 2, - padel_data['pos']['x'])
			cross_point = check_collisions( \
				self.position['x'], self.position['y'], \
				ball_collider['x'], ball_collider['y'],
				player.padel.position['y'] + padel_data['size']['y'] / 2, - padel_data['pos']['x'],
				player.padel.position['y'] - padel_data['size']['y'] / 2, - padel_data['pos']['x']
			)
			logger.log()
			if cross_point['cross'] == True:
				self.position['x'] = cross_point['point']['x']
				self.position['y'] = cross_point['point']['y']
				self.direction['x'] *= -1
				return
		elif ball_destination['x'] > padel_data['pos']['x']:
			player = get_player_in_side('right')
			cross_point = check_collisions( \
				self.position['x'], self.position['y'], \
				ball_collider['x'], ball_collider['y'],
				player.padel.position['y'] + padel_data['size']['y'] / 2, - padel_data['pos']['x'],
				player.padel.position['y'] - padel_data['size']['y'] / 2, - padel_data['pos']['x']
			)
			from pong_game.utils.logger import logger
			if cross_point['cross'] == True:
				logger.debug('point =', cross_point['point'])
				self.position['x'] = cross_point['point']['x']
				self.position['y'] = cross_point['point']['y']
				self.direction['x'] *= -1
				return

		for axis in ['x', 'y']:
			if ball_collider[axis] <= border_collider[axis] \
					and ball_collider[axis] >= -border_collider[axis]:
				self.position[axis] = ball_destination[axis]
			else:
				self.position[axis] = self.direction[axis] * arena_data['size'][axis] / 2 \
					- self.direction[axis] * ball_data['rad']
				self.direction[axis] *= -1
