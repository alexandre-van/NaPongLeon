from ..utils.logger import logger

class Match:
	def __init__(self, teams):
		self.teams = teams
		logger.debug(f"create match || teams : {teams}")
		