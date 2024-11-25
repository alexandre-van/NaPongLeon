
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
	'spd': {
        'x': 50, # speed
        'y': 20
	},
	'rad': 1 # radius
}

padel_data = {
	'pos': {
		'x': 39, # coordinate x
		'y': 0, # coordinate y
        'z': 1.25
	},
	'spd': 30, # speed
	'size': {
        'x': 4,
		'y': 12,
        'z': 4
	},
}

arena_data = {
	'size': {
		'x': 86,
		'y': 64,
        'z': 2
	},
	'wallWidth': 1
}