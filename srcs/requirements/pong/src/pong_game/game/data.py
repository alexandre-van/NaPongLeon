
key_data = {
    'up': 'w',
    'down': 's' 
}

input_data = {
	'up': 1, # event = keydown / key = up
	'down': 2, # event = keydown / key = down
	'stop_up': 3, # event = keyup / key = up
	'stop_down': 4 # event = keyup / key = down
}

ball_data = {
	'pos': {
		'x': 0, # coordinate x
		'y': 0, # coordinate y
        'z': 1
	},
	'spd': 0.5, # speed
	'rad': 1 # radius
}

padel_data = {
	'pos': {
		'x': 36, # coordinate x
		'y': 0, # coordinate y
        'z': 1
	},
	'spd': 1, # speed
	'size': {
        'x': 1,
		'y': 8,
        'z': 2
	},
}

arena_data = {
	'size': {
		'x': 80,
		'y': 60,
        'z': 2
	},
	'wallWidth': 1
}