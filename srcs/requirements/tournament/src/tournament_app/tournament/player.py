from ..utils.logger import logger

class Player:
	def __init__(self, username, consumer, team=None):
		self.username = username
		self.consumer = consumer
		self.team = team
		logger.debug(f"Create player : {username}")

	def set_team(self, team):
		self.team = team