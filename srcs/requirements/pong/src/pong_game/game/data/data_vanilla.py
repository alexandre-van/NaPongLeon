
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
	'rad': 1, # radius
	'pos': {
		'x': 0, # coordinate x
		'y': 0, # coordinate y
        'z': 1
	},
	'spd': {
        'x': 30, # speed
        'y': 30
	}
}

padel_data = {
	'spd': 45, # speed
	'pos': {
		'x': 39, # coordinate x 39
		'y': 0, # coordinate y
        'z': 1.25 # 1.25
	},
	'size': {
        'x': 4,
		'y': 12,
        'z': 4
	}
}

arena_data = {
	'wallWidth': 1,
	'size': {
		'x': 86,
		'y': 64,
        'z': 2
	}
}