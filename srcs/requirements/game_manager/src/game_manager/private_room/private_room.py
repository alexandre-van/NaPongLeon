from django.conf import settings
from ..utils.logger import logger

class GenerateUsername:
	def __init__(self):
		logger.debug("generate_username initialised")
		self.nb_of_players = 0
		
	def generate(self):
		username = "player_" + str(self.nb_of_players)
		self.nb_of_players += 1
		logger.debug(f"username generate: {username}")
		return username
	
class GenerateAIName:
	def __init__(self):
		logger.debug("generate_AI_name initialised")
		self.nb_of_AI = 0
		
	def generate(self):
		AIname = "AI_" + str(self.nb_of_AI)
		self.nb_of_AI += 1
		logger.debug(f"AI name generate: {AIname}")
		return AIname
	
	def isanAI(self, AIname):
		i = 0
		while(i <= self.nb_of_AI):
			tmpAIname = "AI_" + str(i)
			if AIname == tmpAIname:
				return True
			i += 1
		return False
	
class PrivateRoom:
	def __init__(self, username):
		self.host = username
		self.teams = {
			username: [username]
		}
		self.team_size = 0
		self.spectator = []
		self.freeForAll = True 
		self.game_mode = None
		self.GAME_MODES = settings.GAME_MODES
		self.AInameGenerator = GenerateAIName()

	def choice_game_mode(self, game_mode):
		logger.debug(f"choice_game_mode: {game_mode}")
		game_mode_data = self.GAME_MODES.get(game_mode)
		if not game_mode_data:
			logger.debug(f"game_mode does not exist: {game_mode}")
			return self.generate_error_message(f"game_mode does not exist: {game_mode}")
		self.game_mode = game_mode
		new_teams = None

		if not game_mode_data.get('team_names'):
			new_teams = {}
			self.team_size = 1
			self.freeForAll = True
		else:
			new_teams = {team: [] for team in game_mode_data.get('team_names')}
			self.team_size = self.GAME_MODES.get(game_mode).get('team_size')
			self.freeForAll = False
		team_names = list(new_teams.keys())
		index = 0
		for team in self.teams:
			for username in self.teams[team]:
				if not self.freeForAll:
					if index < len(new_teams) and len(new_teams[team_names[index]]) < self.team_size:
						new_teams[team_names[index]].append(username)
					else:
						if not self.AInameGenerator.isanAI(username):
							self.spectator.append(username)
				else:
					new_teams[username] = []
					new_teams[username].append(username)
			index = (index + 1) % len(new_teams)
		self.teams = new_teams
		return self.generate_room_update()

	def add_AI_to_team(self, team):
		logger.debug(f"add_AI_to_team: {team}")
		if team in self.teams:
			logger.debug(f"{len(self.teams[team])} <= {self.team_size}")
			if len(self.teams[team]) < self.team_size:
				AIname = self.AInameGenerator.generate()
				self.teams[team].append(AIname)
				return self.generate_room_update()
			else:
				return self.generate_error_message(f"team is full: {team}")
		elif self.freeForAll and not team:
			AIname = self.AInameGenerator.generate()
			self.teams[AIname] = [AIname]
			return self.generate_room_update()
		else:
			return self.generate_error_message(f"team does not exist: {team}")

	def remove_user_or_AI(self, id):
		logger.debug(f"remove_user_or_AI: {id}")
		if id in self.spectator:
			self.spectator.remove(id)
			return self.generate_room_update()
		elif not self.freeForAll:
			for team in self.teams:
				if id in self.teams[team]:
					self.teams[team].remove(id)
					return self.generate_room_update()
		else:
			if id in self.teams:
				del self.teams[id]
				return self.generate_room_update()

		if not self.AInameGenerator.isanAI(id):
			return self.generate_error_message(f"user not found: {id}")
		else:
			return self.generate_error_message(f"ia not found: {id}")
					

	def start_game(self):
		logger.debug(f"start_game")
	
	def generate_room_update(self):
		return {
			'type': 'room_update',
			'game_mode': self.game_mode,
			'teams': self.teams,
			'team_size': self.team_size,
			'spectator': self.spectator
		}
	
	def generate_error_message(self, msg):
		return {
			'type': 'error_msg',
			'message': msg
		}