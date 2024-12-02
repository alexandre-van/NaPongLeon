from ..utils.logger import logger

class Team:
	def __init__(self, players):
		self.players = players
		self.update_name()
		self.level = 0
		logger.debug(f"{self.name} team created")

	def update_name(self):
		self.name = ",".join(player.username for player in self.players)