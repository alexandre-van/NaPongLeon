from ..utils.logger import logger

class Team:
	def __init__(self, players):
		self.players = players
		self.update_team_name()
		self.score = 0
		logger.debug(f"{self.team_name} team created")

	def update_team_name(self):
		self.team_name = ", ".join(player.username for player in self.players)