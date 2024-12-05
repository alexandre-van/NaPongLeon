from ..utils.logger import logger

class Player:
	def __init__(self, username, nickname, consumer, team=None):
		self.username = username
		self.nickname = nickname
		self.consumer = consumer
		self.team = team
		logger.debug(f"Create player : {username}")

	def set_team(self, team):
		self.team = team

	def export(self):
		return {
			'nickname': self.nickname
		}