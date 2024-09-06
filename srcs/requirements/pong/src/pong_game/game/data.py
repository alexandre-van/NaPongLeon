

input_data = {
	1: 'up', # event = keydown / key = up
	2: 'down', # event = keydown / key = down
	3: 'stop_up', # event = keyup / key = up
	4: 'stop_down' # event = keyup / key = down
}

ball_data = {
	'pos': {
		'x': 0, # coordinate x
		'y': 0 # coordinate y
	},
	'spd': 1, # speed
	'rad': 1 # radius
}

padel_data = {
	'pos': {
		'x': 35, # coordinate x
		'y': 0 # coordinate y
	},
	'spd': 1, # speed
	'size': {
        'x': 1,
		'y': 8,
	},
}

arena_data = {
	'size': {
		'x': 80,
		'y': 60,
	},
	'wallWidth': 1
}