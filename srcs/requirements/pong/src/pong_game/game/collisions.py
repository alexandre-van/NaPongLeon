import math

def get_vector_direction(start, end):
	return { 
		'x': end['x'] - start['x'],
		'y': end['y'] - start['y']
	}


def get_contact_point(ball_center, r, direction, wall):
	if direction['x'] > 0:
		t = (wall['x'] - (ball_center['x'] + r)) / direction['x']
	elif direction['x'] < 0:
		t = (wall['x'] - (ball_center['x'] - r)) / direction['x']
	else:
		return None
	contact = {
		'y': ball_center['y'] + direction['y'] * t,
		'x': wall['x']
	}
	if wall['y']['bottom'] - r <= contact['y'] <= wall['y']['top'] + r:
		return (contact)
	else:
		return None

def get_contact_point_side(ball_center, r, direction, wall):
	from ..utils.logger import logger
	if direction['y'] > 0:
		t = (wall['y'] - (ball_center['y'] + r)) / direction['y']
	elif direction['y'] < 0:
		t = (wall['y'] - (ball_center['y'] - r)) / direction['y']
	else:
		return None
	contact = {
		'y': wall['y'],
		'x': ball_center['x'] + direction['x'] * t
	}
	logger.debug(f'\n\ncontact = {contact}\n')
	logger.debug(f'\nwall = {wall}\n\n')
	if wall['x']['left'] - r <= contact['x'] <= wall['x']['right'] + r:
		logger.debug(f'\n\nCONTACT !\n\n')
		return (contact)
	else:
		return None
