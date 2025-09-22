import httpx
import uuid
from ..utils.logger import logger

class Game:
	def __init__(self, match, game_mode, modifiers):
		self.match = match
		self.game_mode = game_mode
		self.modifiers = modifiers
		self.id = None
		self.service_name = None
		self.limiter = 0
		self.i_limiter = 0
		# Dictionnaire pour mapper usernames et leurs IDs (public et privé)
		self.username_to_id = {}
		self.spectator_connection_id = None

	def export(self):
		return {
			'id': self.id,
			'service_name': self.service_name,
			'spectator_id': self.spectator_connection_id
		}

	def _generate_ids(self, team1, team2):
		"""
		Génère des ID privés et publics pour chaque nom d'utilisateur unique.
		"""
		# Combine les deux équipes dans une liste
		teams = [team1, team2]
		for team in teams:
			for player in team.players:
				# Si l'utilisateur n'a pas encore d'ID, en générer un
				if player.username not in self.username_to_id:
					self.username_to_id[player.username] = {
						'private': str(uuid.uuid4()),
						'public': str(uuid.uuid4()),
						'nickname': player.nickname
					}
					# Associez les IDs du joueur à son consommateur
					player.consumer.game_private_id = self.username_to_id[player.username]['private']


	def _convert_to_public_ids(self, teams):
		"""
		Convertit les noms d'utilisateur en IDs publics dans les équipes.
		"""
		return [
			[self.username_to_id[player]['public'] for player in team]
			for team in teams
		]

	def _convert_to_usernames(self, teams_with_ids):
		"""
		Convertit les IDs publics en noms d'utilisateur dans les équipes.
		"""
		public_to_username = {v['public']: k for k, v in self.username_to_id.items()}
		return [
			[public_to_username[player_id] for player_id in team]
			for team in teams_with_ids
		]

	def _create_special_id_list(self):
		special_id = []
		for username in self.username_to_id:
			special_id.append(self.username_to_id[username])
		self.spectator_connection_id = str(uuid.uuid4())
		special_id.append({
			'private': self.spectator_connection_id,
			'public': 'randomize',
			'nickname': 'spectator'
		})
		return special_id

	async def create_game(self):
		self.i_limiter = self.limiter
		game_manager_service_url = "http://gamemanager:8000/api/game_manager/create_game_api/"
		team1 = self.match.team1
		team2 = self.match.team2
		players_list = [player.username for player in team1.players] + [player.username for player in team2.players]
		teams_list = [
			[player.username for player in team1.players],
			[player.username for player in team2.players]
		]

		# Générer les ID publics et privés pour les joueurs
		self._generate_ids(team1, team2)

		# Convertir les noms d'utilisateur en IDs publics pour les équipes
		teams_with_public_ids = self._convert_to_public_ids(teams_list)
		special_id = self._create_special_id_list()
		logger.debug(f"team ask : {teams_list}")
		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(game_manager_service_url, json={
					'gameMode': self.game_mode,
					'modifiers': ','.join(self.modifiers)	,
					'playersList': [self.username_to_id[player]['public'] for player in players_list],
					'teamsList': teams_with_public_ids,
					'ia_authorizes': False,
					'special_id': special_id
				})
			if response and response.status_code == 201:
				data = response.json().get('data')
				if data:
					self.id = data.get('game_id')
					self.service_name = data.get('service_name')
					return True
			else:
				logger.debug(f'Error api request game_manager, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"game_manager service error: {str(e)}")
		return False

	async def get_game_data(self):
		if self.i_limiter != 0:
			self.i_limiter -= 1
			return None
		self.i_limiter = self.limiter
		game_manager_service_url = f"http://gamemanager:8000/api/game_manager/get_game_data_api/{self.id}/"
		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(game_manager_service_url)
			if response and response.status_code == 200:
				game_data = response.json().get('game_data')

				if game_data:
					return game_data
			else:
				logger.debug(f'Error api request game_manager, response: {response}')
		except httpx.RequestError as e:
			logger.error(f"game_manager service error: {str(e)}")
		return None
