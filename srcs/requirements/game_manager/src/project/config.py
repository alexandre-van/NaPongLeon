import configparser
import os

service_file = os.path.join(os.path.dirname(__file__), '../conf', 'service.ini')
game_mode_file = os.path.join(os.path.dirname(__file__), '../conf', 'game_mode.ini')
service_config = configparser.ConfigParser()
game_mode_config = configparser.ConfigParser()
config = configparser.ConfigParser()
service_config.read(service_file)
game_mode_config.read(game_mode_file)

GAME_MODES = {}
AUTH_SERVICE_URL = service_config['AUTH_SERVICE']['verif_token_url']

for mode in game_mode_config.sections():
	service_name = game_mode_config[mode]['service']
	players = game_mode_config[mode]['players']
	teams = game_mode_config[mode]['teams']
	if service_name in service_config['GAME_SERVICES']:
		service_url = service_config['GAME_SERVICES'][service_name]
		GAME_MODES[mode] = {
			'service_url': service_url,
			'players': int(players),
			'teams': int(teams)
		}