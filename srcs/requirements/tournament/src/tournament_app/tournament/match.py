#from ..utils.logger import logger

class Match:
	def __init__(self, team1, team2):
		self.team1 = team1
		self.team2 = team2
		self.status = 'Waiting'
		self.score = {
			team1: 0,
			team2: 0,
		}
		self.winner = None
		print(f"create match || team : {team1.name} vs {team2.name}")
	
	def print(self):
		return self.team1.name + "vs" + self.team2.name
		