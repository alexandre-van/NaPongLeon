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
	if wall['y']['bottom'] <= contact['y'] <= wall['y']['top']:
		return (contact)
	else:
		return None
