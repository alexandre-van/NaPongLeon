from ..utils.logger import logger

class Match:
	def __init__(self, branch, team1, team2):
		self.branch = branch
		self.team1 = team1
		self.team2 = team2
		self.team1.new_match(self)
		self.team2.new_match(self)
		self.status = 'Waiting'
		self.score = {
			team1.name: 0,
			team2.name: 0,
		}
		self.winner = None
		logger.debug(f"create match || team : {team1.name} vs {team2.name}")
	
	def export(self):
		return {
			'id': self.id,
			'team1': self.team1.export() if self.team1 else None,
			'team2': self.team2.export() if self.team2 else None,
			'status': self.status,
			'score': self.score,
			'winner': self.winner
		}
		