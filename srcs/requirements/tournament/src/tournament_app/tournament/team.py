from ..utils.logger import logger
from .status import teams_status

class Team:
	def __init__(self, players):
		self.players = players
		self.update_name()
		self.level = 0
		self.status = "Waiting..."
		self.current_branch = None
		self.matchs = []
		logger.debug(f"{self.name} team created")

	def update_name(self):
		self.name = ", ".join(player.nickname for player in self.players)

	def set_current_branch(self, new_current_branch):
		self.current_branch = new_current_branch
		self.level = self.current_branch.level

	def new_match(self, match):
		self.matchs.append(match)
		self.set_status("Waiting the match...")

	def set_status(self, new_status):
		self.status = teams_status[new_status] if teams_status.get(new_status) else new_status
		list(player.set_status(new_status) for player in self.players)

	async def update(self):
		for player in self.players:
			await player.update()

	def export(self):
		return {
			'name': self.name,
			'players': list(player.export() for player in self.players),
			'level': self.level,
			'status': self.status,
			'current_cell_id': self.current_branch.id
		}