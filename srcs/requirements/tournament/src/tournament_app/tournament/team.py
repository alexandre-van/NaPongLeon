from ..utils.logger import logger

class Team:
	def __init__(self, players):
		self.players = players
		self.update_name()
		self.level = 0
		self.status = "Waiting..."
		self.matchs = []
		logger.debug(f"{self.name} team created")

	def update_name(self):
		self.name = ", ".join(player.nickname for player in self.players)

	def set_level(self, level):
		self.level = level

	def new_match(self, match):
		self.matchs.append(match)
		self.set_status("Waiting the match")

	def set_status(self, new_status):
		self.status = new_status
		(player.set_status(new_status) for player in self.players)

	def export(self):
		return {
			'name': self.name,
			'players': list(player.export() for player in self.players),
			'level': self.level,
			'status': self.status
		}