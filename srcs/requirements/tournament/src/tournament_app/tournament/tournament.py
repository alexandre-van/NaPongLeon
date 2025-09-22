from ..utils.logger import logger
from ..tournament_manager.data import game_modes_data
from .data import modifiers_data
from .team import Team
from .tree import Tree
from .player import Player
import random

class Tournament:
	def __init__(self, players_dict, game_mode, modifiers_list):
		self.game_mode = game_mode
		modifiers = self.init_modifers(modifiers_list)
		self.modifiers = modifiers['tournament']
		self.game_modifiers = modifiers['game']
		self.players = self.init_players(players_dict)
		self.teams = self.init_teams()
		self.tree = Tree(self.teams)
		self.tree.init_matchs(game_mode, self.game_modifiers)

	#tournament update

	async def update(self):
		await self.tree.update()
		if self.tree.root.bench:
			return self.tournament_end()
		return {
			'type': 'tournament_update',
			'tree': self.tree.export(),
			'teams': list(team.export() for team in self.teams),
		}

	# export data

	def export_data(self):
		return {
			'game_mode': game_modes_data[self.game_mode],
			'modifers': self.modifiers,
			'tree': self.tree.export(),
			'teams': list(team.export() for team in self.teams)
		}
	
	def export_teams(self):
		teams_data = {}
		for team in self.teams:
			players_list = []
			for player in team.players:
				players_list.append(player.username)
			teams_data[team.name] = players_list
		return teams_data
	
	
	def tournament_end(self):
		return {
			'type': 'tournament_end',
			'tree': self.tree.export(),
			'teams': list(team.export() for team in self.teams),
			'team': self.tree.root.bench.export(),
			'score': 0
		}


	# init

	def init_players(self, players_dict):
		usernames = list(players_dict.keys())
		random.shuffle(usernames)
		players = {username: players_dict[username] for username in usernames}
		for username in players_dict:
			nickname = players_dict[username]['nickname']
			consumer = players_dict[username]['consumer']
			players[username] = Player(username, nickname, consumer)
		return players

	def init_teams(self):
		teams = []
		teams_distrib = []
		i_distrib = 0
		nb_of_players = len(self.players)
		team_size = game_modes_data[self.game_mode]['team_size']
		for username in self.players:
			if i_distrib >= nb_of_players / team_size:
				i_distrib = 0
			if len(teams_distrib) <= i_distrib:
				teams_distrib.append([])
			if len (teams_distrib[i_distrib]) < team_size:
				teams_distrib[i_distrib].append(self.players[username])
			i_distrib += 1
		for team_distrib in teams_distrib:
			teams.append(Team(team_distrib))
		return teams
	
	def init_modifers(self, modifiers_list):
		modifiers = {
			'tournament': [],
			'game': []
		}
		if not modifiers_list:
			return modifiers
		for mod in modifiers_list:
			if mod in modifiers_data:
				modifiers['tournament'].append(mod)
			else:
				modifiers['game'].append(mod)
		return modifiers