from ..utils.logger import logger

class Player:
	def __init__(self, username, nickname, consumer, team=None):
		self.username = username
		self.nickname = nickname
		self.consumer = consumer
		self.status = 'Waiting...'
		self.team = team
		logger.debug(f"Create player : {username}")

	def set_team(self, team):
		self.team = team

	def set_status(self, new_status):
		self.status = new_status

	def export(self):
		return {
			'nickname': self.nickname,
			'status': self.status
		}