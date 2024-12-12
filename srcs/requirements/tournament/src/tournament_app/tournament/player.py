from ..utils.logger import logger
from .status import players_status

class Player:
	def __init__(self, username, nickname, consumer, team=None):
		self.username = username
		self.nickname = nickname
		if nickname == None:
			self.nickname = username
		self.consumer = consumer
		self.status = 'Waiting...'
		self.team = team

	def set_team(self, team):
		self.team = team

	def set_status(self, new_status):
		self.status = players_status[new_status] if players_status.get(new_status) else new_status

	async def update(self):
		pass

	def export(self):
		return {
			'nickname': self.nickname,
			'status': self.status
		}