from ..utils.logger import logger
import json
import asyncio
from .game_manager import game_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from ..utils.decorators import auth_required

class GameConsumer(AsyncWebsocketConsumer):
	ready_queue = asyncio.Lock()

	# CONNECT
	@auth_required
	async def connect(self, username=None):
		path = self.scope['path']
		segments = path.split('/')
		self.room = None
		self.game_id = None
		self.is_closed = False
		self.admin_id = None
		self.username = username
		self.can_be_disconnected = True
		special_id = None
		if len(segments) >= 4:
			self.game_id = segments[3]
		if len(segments) >= 6:
			special_id = segments[4]
			logger.debug(f'special_id = {special_id}')
		if special_id:
			self.username = game_manager.special_connection(special_id, self.game_id)
			if not self.username:
				self.username = 'admin'
				self.admin_id = special_id
		if not self.username and not self.admin_id:
			logger.warning(f'An unauthorized connection has been received')
			return
		logger.debug(f'{self.username} tries to connect to the game: {self.game_id}')

		if game_manager.get_room(self.game_id) is not None:
			await self.new_users()
		else:
			logger.debug(f'{self.game_id} does not exist')
			await self.send_message({
				'error': '404',
				'message': f'{self.game_id} does not exist'
			})

	async def new_users(self):
		logger.debug("new_user")
		self.ready = False
		if self.admin_id:
			self.room = game_manager.add_admin(self.admin_id, self, self.game_id)
			if self.room is None:
				return
			await self.accept()
			await self.channel_layer.group_add(self.admin_id, self.channel_name)
			asyncio.create_task(self.status_loop())
			logger.debug(f"Admin is connected !")

			return
		else:
			self.room = game_manager.add_user(self.username, self, self.game_id)
			if self.room is None:
				return
			await self.send_user_connection()
			await self.accept()
		if self.room and self.room['status'] == 'startup' and self.room['game_instance'] \
			and self.username in self.room['players']:
			await self.startup()
		elif self.room and self.room['status'] != 'waiting' and self.room['game_instance'] \
			and self.username not in self.room['players']:
			await self.add_spectator()
		else:
			await self.send_message({
				'type': 'waiting_room',
			})

	async def startup(self):
		logger.debug(" admin as been disconnected")
		game_manager.update_status('loading', self.game_id)
		admin = self.room['admin']
		for player in self.room['players']:
			logger.debug(f"add {player} to channel")
			await self.channel_layer.group_add(self.game_id, self.room['players'][player].channel_name)
		for spectator in self.room['spectator']:
			await self.channel_layer.group_add(self.game_id, self.room['spectator'][spectator].channel_name)
		await self.send_game_status(admin['id'], self.game_id, 'loading')
		game_data = self.room['game_instance'].export_data()
  

		# Remplacement des IDs par les nicknames
		self.remplacenickname(game_data)
	
		#game_data = replace_ids_with_nicknames(game_data)
		logger.debug(f"GAME DATA : {game_data}")
	
		#faire en sorte de chamger game_data pour que je puisse remplacer l'id par le nickname present dans le dictionnaire special id
  
		await self.send_export_teams(admin['id'], game_data['teams'])
		await self.send_export_data(self.game_id, game_data)
		logger.debug(f'Export data')

	def remplacenickname(self, game_data):
		special_ids = self.room.get('special_id', [])
		if special_ids:
			id_to_nickname = {id_map['public']: id_map['nickname'] for id_map in special_ids if 'public' in id_map and 'nickname' in id_map}

			logger.debug(f"ID TO NICKNAME : {id_to_nickname}")
			logger.debug(f"GAME DATA : {game_data}")

			def replace_ids_with_nicknames(data):
				if isinstance(data, dict):
						# Parcourt récursivement les dictionnaires
					return {k: replace_ids_with_nicknames(v) for k, v in data.items()}
				elif isinstance(data, list):
						# Parcourt récursivement les listes et remplace les IDs
					return [id_to_nickname.get(item, item) for item in data]
				return data

			game_data['teams'] = {k: replace_ids_with_nicknames(v) for k, v in game_data['teams'].items()}

	async def add_spectator(self):
		logger.debug(f"{self.username} is here")
		game_data = self.room['game_instance'].export_data()
		self.remplacenickname(game_data)
		await self.send_message({
			'type': "export_data",
			'data': game_data
		})

	async def send_user_connection(self):
		type_name = None
		if self.username in self.room['players']:
			type_name = 'player_connection'
		elif self.username in self.room['spectator']:
			type_name = 'spectator_connection'
		else:
			return
		admin = self.room['admin']
		groups = [admin['id'], self.game_id]
		await self.send_to_multiple_groups(groups, {
				'type': type_name,
				'username': self.username
		})

	# DISCONNECT

	async def disconnect(self, close_code):
		if not self.room or self.is_closed == True:
			return
		self.is_closed = True
		await self.channel_layer.group_discard(self.game_id, self.channel_name)
		if self.admin_id == self.room['admin']['id']:
			logger.debug(f"admin as been disconnected")
			await self.game_end()
			return
		if self.username in self.room['players']:
			admin = self.room['admin']
			logger.debug(f"{self.username} as been disconnected")
			if self.room['game_instance'] and self.room['status'] == 'running':
				teams = self.room['game_instance'].players_in_side
				score = self.room['game_instance'].score
				opponent_team = None
				for teamname in teams:
					logger.debug(f'team check : {self.username} is in {teamname}({teams[teamname]}) ?')
					if self.username not in list(player.username for player in teams[teamname]):
						opponent_team = teamname
						logger.debug(f'opponant team : {self.username} in {teamname}.')
						break
				logger.debug(f"{opponent_team}: {score[opponent_team]}")
				await self.channel_layer.group_send( self.game_id,
					{
						'type': 'send_state',
						'state': self.room['game_instance'].give_up(opponent_team)
					}
				)
				if self.room['status'] != 'aborted':
					game_manager.update_status('aborted', self.game_id)
					await self.send_game_finished(opponent_team, score[opponent_team], 'aborted')
			await self.game_end()
		else:
			if self.username in self.room['spectator']:
				await self.send_user_disconnection()
				game_manager.remove_user(self.username, self.game_id)

	async def disconnect_all_users(self):
		logger.debug('disconnect_all_user')
		for player in self.room['players']:
			try:
				self.room['players'][player].is_closed = True
				await self.channel_layer.group_discard(self.game_id, self.room['players'][player].channel_name)
				await self.room['players'][player].close()
			except Exception as e:
				logger.error(f"Error closing player connection: {e}")
		for spectator in self.room['spectator']:
			try:
				self.room['spectator'][spectator].is_closed = True
				await self.channel_layer.group_discard(self.game_id, self.room['spectator'][spectator].channel_name)
				await self.room['spectator'][spectator].close()
			except Exception as e:
				logger.error(f"Error closing spectator connection: {e}")

	async def send_user_disconnection(self):
		type_name = None
		if self.username in self.room['players']:
			type_name = 'player_disconnection'
		elif self.username in self.room['spectator']:
			type_name = 'spectator_disconnection'
		else:
			return
		admin = self.room['admin']
		groups = [admin['id'], self.game_id]
		await self.send_to_multiple_groups(groups, {
				'type': type_name,
				'username': self.username
		})

	async def disconnect_admin(self):
		logger.debug('disconnect_admin')
		try:
			admin = self.room['admin']
			while True:
				if admin['consumer'].can_be_disconnected == True:
					admin['consumer'].is_closed = True
					await self.channel_layer.group_discard(self.game_id, self.room['admin']['consumer'].channel_name)
					await self.room['admin']['consumer'].close()
					return
				else:
					await asyncio.sleep(1)
		except Exception as e:
			logger.error(f"Error closing admin connection: {e}")

	async def game_end(self):
		logger.debug("game_end")
		await self.disconnect_all_users()
		await self.disconnect_admin()
		game_manager.remove_room(self.game_id)

	# RECEIVE

	async def receive(self, text_data):
		if not self.room:
			return
		try:
			data = json.loads(text_data)
			data_type = data['type']
			game_room = self.room['game_instance']
			if game_room:
				if data_type == 'move' and self.username in self.room['players']:
					game_room.input_players(self.username, data['input'])
				elif data_type == 'ready':
					if self.username in self.room['players']:
						async with GameConsumer.ready_queue:
							await self.game_start()
					elif self.username in self.room['spectator']:
						await self.game_start_spectator()
		except json.JSONDecodeError:
			logger.error("Failed to decode JSON data")
		except Exception as e:
			logger.error(f"Unexpected error: {e}")

	async def game_start(self):
		self.ready = True
		for player in self.room['players']:
			if self.room['players'][player].ready == False:
				return
		if self.room['status'] == 'loading':
			game_manager.update_status('running', self.game_id)
			admin = self.room['admin']
			await self.send_game_status(admin['id'], None, 'in_progress')
			await self.channel_layer.group_send(self.game_id, {
				'type': 'send_state',
				'state': {
					'type': 'game_start'
				}
			})
			asyncio.create_task(self.game_loop(self.game_id))
			logger.debug(f'Game start')
	
	async def game_start_spectator(self):
		self.ready = True
		if self.room['status'] == 'running':
			await self.channel_layer.group_add(self.game_id, self.channel_name)
			await self.send_message({
				'type': 'game_start'
			})
			logger.debug(f'Spectate start for {self.username}')



	# GAME LOOP

	async def game_loop(self, game_id):
		if not self.room:
			return
		logger.debug("Game loop is running")
		while game_manager.get_room(self.game_id):
			game = self.room['game_instance']
			if game:
				game_state = game.update()
				await self.channel_layer.group_send(
					game_id,
					{
						'type': 'send_state',
						'state': game_state
					}
				)
				if game_state['type'] == 'scored':
					logger.debug('scored')
					await self.send_update_score(game_state['team'], game_state['score'])
				elif game_state['type'] == 'game_end':
					game_manager.update_status('finished', self.game_id)
					await self.send_game_finished(game_state['team'], game_state['score'], 'finished')
					await self.game_end()
					return
				await asyncio.sleep(0.025)
			else:
				break

	async def send_update_score(self, team, score):
		admin = self.room['admin']
		await self.channel_layer.group_send(admin['id'], {
				'type': "send_state",
				'state': {
					'type': "update_score",
					'team': team,
					'score': score
				}
			})
		
	async def send_game_finished(self, team, score, status):
		admin = self.room['admin']
		admin['consumer'].can_be_disconnected = False
		await self.channel_layer.group_send(admin['id'], {
				'type': "send_state",
				'state': {
					'type': "export_status",
					'status': status,
					'team': team,
					'score': score
				}
			})

	# STATUS_LOOP
	async def status_loop(self):
		while self.room['status'] != 'aborted' and self.room['status'] != 'finished':
			logger.debug("HELLO")
			await asyncio.sleep(1)

		if self.room['status'] == 'aborted' and self.room['teamlist']:
			logger.debug(f"THE JUDGEMENT")

			# Récupérer les équipes et les joueurs
			teamlist = self.room['teamlist']
			players = self.room['players']

			# Initialisation des variables pour suivre les résultats
			team_absents = {"left": 0, "right": 0}
			team_presents_ready = {"left": 0, "right": 0}

			# Calcul du nombre de joueurs absents et présents prêts pour chaque équipe
			for idx, team_players in enumerate(teamlist):
				team_name = "left" if idx == 0 else "right"
				absents = 0
				presents_ready = 0
				logger.debug(f"{team_name} check :")
				for player in team_players:
					if player not in players:  # Joueur absent
						logger.debug(f"{player} is absent")
						absents += 1
					else:  # Joueur présent
						consumer = players[player]
						if consumer.ready:  # Joueur présent et prêt
							logger.debug(f"{player} is ready")
							presents_ready += 1
						else:
							logger.debug(f"{player} not ready")

				team_absents[team_name] = absents
				team_presents_ready[team_name] = presents_ready

			# Déterminer l'équipe gagnante en fonction des absents
			min_absents = min(team_absents.values())
			teams_with_min_absents = [team for team, count in team_absents.items() if count == min_absents]

			if len(teams_with_min_absents) == 1:  # Une seule équipe a le moins d'absents
				winning_team = teams_with_min_absents[0]
			else:  # Égalité dans les absents, vérifier les joueurs prêts
				max_ready = max(team_presents_ready.values())
				teams_with_max_ready = [team for team, count in team_presents_ready.items() if count == max_ready]

				if len(teams_with_max_ready) == 1:  # Une seule équipe a le plus de joueurs prêts
					winning_team = teams_with_max_ready[0]
				else:  # Égalité dans les joueurs prêts
					winning_team = None

			# Annoncer le résultat
			if winning_team:
				logger.debug(f"win_team = {winning_team}")
				await self.send_game_finished(winning_team, None, 'aborted')
		logger.debug("orf")
		await self.game_end()



	# UTILS

	async def send_export_data(self, game_id, data):
		await self.channel_layer.group_send(game_id, {
				'type': "send_state",
				'state': {
					'type': "export_data",
					'data': data
				}
			})
		
	async def send_export_teams(self, admin_id, teams):
		await self.channel_layer.group_send(admin_id, {
				'type': "send_state",
				'state': {
					'type': "export_teams",
					'teams': teams
				}
			})

	async def send_game_status(self, admin_id, game_id, status):
		logger.debug(f"export status {status}")
		groups = []
		if admin_id:
			groups.append(admin_id)
		if game_id:
			groups.append(game_id)
		await self.send_to_multiple_groups(groups, {
				'type': 'export_status',
				'status': status
		})


	async def send_to_multiple_groups(self, groups, message):
		for group in groups:
			if group:  # S'assurer que le nom du groupe est valide
				try:
					logger.debug(f"Sending message to group: {group}\nmessage: {message}")
					await self.channel_layer.group_send(
						group, {
							'type': 'send_state',
							'state': message
						}
					)
				except Exception as e:
					logger.error(f"Failed to send message to group {group}: {e}")
			else:
				logger.error("Invalid group name detected")


	async def send_message(self, message):
		try:
			if self.is_closed is False:
				await self.send(text_data=json.dumps(message))
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send message: {e}")

	# STATE EVENT

	async def send_state(self, event):
		try:
			if self.is_closed is False:
				if event['state']['type'] == 'export_data':
					logger.debug(f"{self.username} receive export data")
				await self.send(text_data=json.dumps(event['state']))
				self.can_be_disconnected = True
			else:
				logger.debug(f"{self.username} consumer want send new statde but is closed")
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send state: {e}")

