from ..utils.logger import logger
from .status import match_status
from .game import Game

class Match:
	def __init__(self, branch, team1, team2, game_mode, modifiers):
		self.game = Game(self, game_mode, modifiers)
		self.branch = branch
		self.team1 = team1
		self.team2 = team2
		self.team1.new_match(self)
		self.team2.new_match(self)
		self.launch_cooldown = 9
		self.status = f'Begin in {self.launch_cooldown}s...'
		self.team_in_game = {
			team1.name: None,
			team2.name: None,
		}
		self.score = {
			team1.name: 0,
			team2.name: 0,
		}
		self.winner = None
		logger.debug(f"create match || team : {team1.name} vs {team2.name}")
	
	async def update(self):
		if self.game is None:
			return
		if self.launch_cooldown > 0:
			self.status = f'Begin in {self.launch_cooldown}s...'
			self.set_teams_status(f"Match begin in {self.launch_cooldown}s...")
			self.launch_cooldown -= 3
		elif self.launch_cooldown == 0:
			self.launch_cooldown -= 3
			game_is_created = await self.game.create_game()
			if game_is_created:
				self.set_status("waiting")
			else:
				self.status = "Aborted"
		else:
			game_data = await self.game.get_game_data()
			logger.debug(f"Match {self.team1.name} vs {self.team2.name} | game_data = {game_data}")
			if game_data:
				self.set_status(game_data['status'])
				score = game_data['scores']
				teamsIngame = None
				i = 0
				teams = [self.team1, self.team2]
				teamsIngame = ['left', 'right']
				for teamname in teamsIngame:
					if teamname in score:
						self.score[teams[i].name] = score[teamname]
					self.team_in_game[teams[i].name] = teamname
					winner = game_data['winner']
					if teamname == winner:
						self.set_winner(teams[i], teams[(i + 1) % 2])
					i += 1
		if self.status == "Game finished" or self.status == "Game aborted":
			self.game = None

	def set_winner(self, win_team, lose_team):
		logger.debug(f"win team: {win_team.name}, lose team: {lose_team.name}")
		self.winner = win_team
		lose_team.set_status("defeated")

	def set_status(self, status):
		self.status = match_status[status] if match_status.get(status) else status
		self.team1.set_status(status)
		self.team2.set_status(status)

	def set_teams_status(self, status):
		self.team1.set_status(status)
		self.team2.set_status(status)

	def export(self):
		return {
			'game': self.game.export() if self.game else None,
			'team1': self.team1.export() if self.team1 else None,
			'team2': self.team2.export() if self.team2 else None,
			'status': self.status,
			'team_in_game': self.team_in_game,
			'score': self.score,
			'winner': self.winner.name if self.winner else None
		}