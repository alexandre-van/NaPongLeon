from django.conf import settings
from ..utils.logger import logger

class GenerateUsername:
	def __init__(self):
		logger.debug("generate_username initialised")
		self.nb_of_players = 0
		
	def generate(self):
		username = "player_" + str(self.nb_of_players)
		self.nb_of_players += 1
		logger.debug(f"username generate : {username}")
		return username
	
class PrivateRoom:
	def __init__(self, username):
		self.host = username

	def choice_game_mode(self, game_mode):
		logger.debug(f"choice_game_mode :{game_mode}")

	def add_ia_to_team(self, team):
		logger.debug(f"add_ia_to_team :{team}")

	def remove_ia_to_team(self, team):
		logger.debug(f"remove_ia_to_team :{team}")

	def start_game(self):
		logger.debug(f"start_game")