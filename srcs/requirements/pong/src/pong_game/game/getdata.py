import copy

def get_data(modifiers, data_name):
	data = get_data_vanilla(data_name)
	if modifiers == None or data_name == 'key_data' or data_name == 'input_data':
		return data
	if 'so_long' in modifiers:
		data = get_data_modifer_so_long(data, data_name)
	if 'small_arena' in modifiers:
		data = get_data_modifer_small_arena(data, data_name)
	if 'elusive' in modifiers:
		data = get_data_modifer_elusive(data, data_name)
	if 'border' in modifiers:
		data = get_data_modifer_border(data, data_name)
	if 'perfection' in modifiers:
		data = get_data_modifer_perfection(data, data_name)
	return data

def get_data_vanilla(data_name):
	from .data.data_vanilla import key_data, input_data, ball_data, padel_data, arena_data
	data_dict = {
		'key_data': key_data,
		'input_data': input_data,
		'ball_data': ball_data,
		'padel_data': padel_data,
		'arena_data': arena_data
	}
	data = copy.deepcopy(data_dict.get(data_name))
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'data_vanilla'.")
	return data

def get_data_modifer_so_long(data, data_name):
	from .data.data_modifier_so_long import ball_data, padel_data, arena_data
	select_data(data, data_name, ball_data, padel_data, arena_data)
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'so_long'.")
	return data

def get_data_modifer_small_arena(data, data_name):
	from .data.data_modifier_small_arena import ball_data, padel_data, arena_data
	select_data(data, data_name, ball_data, padel_data, arena_data)
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'small_arena'.")
	return data

def get_data_modifer_elusive(data, data_name):
	from .data.data_modifier_elusive import ball_data, padel_data, arena_data
	select_data(data, data_name, ball_data, padel_data, arena_data)
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'elusive'.")
	return data

def get_data_modifer_border(data, data_name):
	from .data.data_modifier_border import ball_data, padel_data, arena_data
	select_data(data, data_name, ball_data, padel_data, arena_data)
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'border'.")
	return data

def get_data_modifer_perfection(data, data_name):
	from .data.data_modifier_perfection import ball_data, padel_data, arena_data
	select_data(data, data_name, ball_data, padel_data, arena_data)
	if data is None:
		raise ValueError(f"Data with name '{data_name}' not found in 'border'.")
	return data

def select_data(data, data_name, ball_data, padel_data, arena_data):
	if data_name == 'ball_data':
		modifer_data(data, ball_data)
	elif data_name == 'padel_data':
		modifer_data(data, padel_data)
	elif data_name == 'arena_data':
		modifer_data(data, arena_data)

def modifer_data(data1, data2):
	is_first = True
	for data_name in data1:
		if is_first:
			data1[data_name] *= data2[data_name]
			is_first = False
		else:
			for sub_data_name in data1[data_name]:
				data1[data_name][sub_data_name] *= data2[data_name][sub_data_name]
