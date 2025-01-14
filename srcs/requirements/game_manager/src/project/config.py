import configparser
import os

service_file = os.path.join(os.path.dirname(__file__), '../conf', 'service.ini')
game_mode_file = os.path.join(os.path.dirname(__file__), '../conf', 'game_mode.ini')
if not os.path.isfile(service_file):
    raise Exception(f"{service_file} is missing")
if not os.path.isfile(game_mode_file):
    raise Exception(f"{game_mode_file} is missing")
service_config = configparser.ConfigParser()
game_mode_config = configparser.ConfigParser()
service_config.read(service_file)
game_mode_config.read(game_mode_file)

service_required_sections = ['AUTH_SERVICE', 'GAME_SERVICES_URL_NEW_GAME', 'GAME_SERVICES_URL_ABORT_GAME', 'GAME_SERVICES_WS']
for section in service_required_sections:
    if section not in service_config:
        raise Exception(f"{service_file}: {section} section is missing")

GAME_MODES = {}
AUTH_SERVICE_URL = service_config['AUTH_SERVICE'].get('verif_token_url')
if (not AUTH_SERVICE_URL):
	raise Exception(f"{service_file}: verif_token_url is missing")

for mode in game_mode_config.sections():
	service_name = game_mode_config[mode].get('service')
	if not service_name:
		raise Exception(f"{game_mode_file}: service name is missing for {mode} game mode")
	number_of_players = game_mode_config[mode].get('number_of_players')
	if number_of_players and (not number_of_players.isdigit() or int(number_of_players) <= 0):
		raise Exception(f"{game_mode_file}: number_of_players must be a positive integer for {mode} game mode")
	if number_of_players:
		number_of_players = int(number_of_players)
	team_names = game_mode_config[mode].get('team_names')
	if team_names:
		team_names = team_names.split(',')
	team_size = game_mode_config[mode].get('team_size')
	if team_names and not team_size:
		raise Exception(f"{game_mode_file}: team_size is missing for {mode} game mode")
	if team_size:
		if not team_size.isdigit() or int(team_size) <= 0:
			raise Exception(f"{game_mode_file}: team_size must be a positive integer for {mode} game mode")
		team_size = int(team_size)
	modifier_list = game_mode_config[mode].get('modifier_list')
	if modifier_list:
		modifier_list = modifier_list.split(',')
	if service_name in service_config['GAME_SERVICES_URL_NEW_GAME'] \
		and service_name in service_config['GAME_SERVICES_URL_ABORT_GAME'] \
		and service_name in service_config['GAME_SERVICES_WS']:
		service_url_new_game = service_config['GAME_SERVICES_URL_NEW_GAME'][service_name]
		service_url_abort_game = service_config['GAME_SERVICES_URL_ABORT_GAME'][service_name]
		service_ws = service_config['GAME_SERVICES_WS'][service_name]
		service_ai = None
		if service_name in service_config['AI_SERVICES']:
			service_ai = service_config['AI_SERVICES'][service_name]
		GAME_MODES[mode] = {
			'service_name': service_name,
			'service_url_new_game': service_url_new_game,
			'service_url_abort_game': service_url_abort_game,
			'service_ws': service_ws,
			'service_ai': service_ws,
			'number_of_players': number_of_players,
			'team_names': team_names,
			'team_size': team_size,
			'modifier_list': modifier_list
		}
	else:
		raise Exception(f"{service_file}: {service_name} is missing in one of the GAME_SERVICE sections of the {mode} game mode")
