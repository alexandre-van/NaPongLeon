import configparser
import os

config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

config = configparser.ConfigParser()
config.read(config_file)

GAME_MODES = {key: config.getint('GAME_MODES', key) for key in config['GAME_MODES']}
