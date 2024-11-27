from ..utils.logger import logger

class Branch:
	def __init__(self, team1, team2):
		self.team1 = team1
		self.team2 = team2
		logger.debug(f"create branch : {team1.team_name} vs {team2.team_name}")