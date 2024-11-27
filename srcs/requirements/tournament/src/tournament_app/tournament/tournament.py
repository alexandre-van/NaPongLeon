from ..utils.logger import logger
from ..data import game_modes
from .team import Team

class Tournament:
	def __init__(self, players, game_mode, modifiers, teams = None):
		self.players = players
		self.game_mode = game_mode
		self.modifers = modifiers
		self.teams = self.init_teams(teams)

	def update(self):
		pass

	def init_teams(self, teams):
		if not self.teams:
			self.teams = {}
			team_size = game_modes[self.game_mode]['team_size']
			players_in_team = []
			while 1:
				while len(players_in_team) != team_size:

			team = Team(players_in_team)
			self.teams[team.team_name] = team
