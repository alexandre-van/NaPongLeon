from ..utils.logger import logger
import json
import asyncio
from .tournament_manager import tournament_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from ..utils.decorators import auth_required

class TournamentConsumer(AsyncWebsocketConsumer):
	ready_queue = asyncio.Lock()

	# CONNECT
	@auth_required
	async def connect(self, username=None, nickname=None):
		path = self.scope['path']
		segments = path.split('/')
		self.room = None
		self.tournament_id = None
		self.is_closed = False
		self.admin_id = None
		self.username = username
		self.nickname = nickname
		self.game_private_id = None
		self.can_be_disconnected = True
		special_id = None
		if len(segments) >= 4:
			self.tournament_id = segments[3]
		if len(segments) >= 6:
			special_id = segments[4]
		if special_id:
			self.username = tournament_manager.special_connection(special_id, self.tournament_id)
			if not self.username:
				self.username = 'admin'
				self.admin_id = special_id
		if not self.username and not self.admin_id:
			logger.warning(f'An unauthorized connection has been received')
			return
		logger.debug(f'{self.username} tries to connect to the tournament: {self.tournament_id}')
		if tournament_manager.get_room(self.tournament_id) is not None:
			await self.new_users()
		else:
			logger.debug(f'{self.tournament_id} does not exist')
			await self.send_message({
				'error': '404',
				'message': f'{self.tournament_id} does not exist'
			})

	async def new_users(self):
		self.ready = False
		if self.admin_id:
			self.room = tournament_manager.add_admin(self.admin_id, self, self.tournament_id)
			if self.room is None:
				return
			await self.accept()
			await self.channel_layer.group_add(self.admin_id, self.channel_name)
			asyncio.create_task(self.status_loop())
			logger.debug(f"Admin is connected !")

			return
		else:
			self.room = tournament_manager.add_user(self.username, self.nickname, self, self.tournament_id)
			if self.room is None:
				return
			await self.send_user_connection()
			await self.accept()
		if self.room and self.room['status'] == 'startup' and self.room['tournament_instance'] \
			and self.username in self.room['players']:
			await self.startup()
		elif self.room and self.room['status'] != 'waiting' and self.room['tournament_instance'] \
			and self.username not in self.room['players']:
			await self.add_spectator()
		else:
			await self.send_message({
				'type': 'waiting_room',
			})

	async def startup(self):
		tournament_manager.update_status('loading', self.tournament_id)
		admin = self.room['admin']
		for player in self.room['players']:
			playerConsumer = self.room['players'][player]['consumer']
			await self.channel_layer.group_add(self.tournament_id, playerConsumer.channel_name)
		for spectator in self.room['spectator']:
			spectatorConsumer = self.room['spectator'][spectator]['consumer']
			await self.channel_layer.group_add(self.tournament_id, spectatorConsumer.channel_name)
		await self.send_tournament_status(admin['id'], self.tournament_id, 'loading')
		tournament_data = self.room['tournament_instance'].export_data()
		teams = self.room['tournament_instance'].export_teams()
		await self.send_export_teams(admin['id'], teams)
		await self.send_export_data(self.tournament_id, tournament_data)

	async def add_spectator(self):
		await self.send_message({
			'type': "export_data",
			'data': self.room['tournament_instance'].export_data()
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
		groups = [admin['id'], self.tournament_id]
		await self.send_to_multiple_groups(groups, {
				'type': type_name,
				'username': self.username
		})

	# DISCONNECT

	async def disconnect(self, close_code):
		if not self.room or self.is_closed == True:
			return
		self.is_closed = True
		await self.channel_layer.group_discard(self.tournament_id, self.channel_name)
		if self.admin_id == self.room['admin']['id']:
			await self.tournament_end()
			return
		else:
			if self.username in self.room['players']:
				await self.send_user_disconnection()
			elif self.username in self.room['spectator']:
				await self.send_user_disconnection()
				tournament_manager.remove_user(self.username, self.tournament_id)

	async def disconnect_all_users(self):
		logger.debug('disconnect_all_user')
		for player in self.room['players']:
			try:
				player_consumer = self.room['players'][player]['consumer']
				player_consumer.is_closed = True
				await self.channel_layer.group_discard(self.tournament_id, player_consumer.channel_name)
				await player_consumer.close()
			except Exception as e:
				logger.error(f"Error closing player connection: {e}")
		for spectator in self.room['spectator']:
			try:
				spectatorConsumer = self.room['spectator'][spectator]['consumer']
				spectatorConsumer.is_closed = True
				await self.channel_layer.group_discard(self.tournament_id, spectatorConsumer.channel_name)
				await spectatorConsumer.close()
			except Exception as e:
				logger.error(f"Error closing spectator connection: {e}")

	async def send_user_disconnection(self):
		type_name = None
		if self.username in self.room['players']:
			type_name = 'player_disconnection'
			del self.room['players'][self.username]
		elif self.username in self.room['spectator']:
			type_name = 'spectator_disconnection'
		else:
			return
		if len(self.room['players']) < 1:
			await self.tournament_end()
			return
		admin = self.room['admin']
		groups = [admin['id'], self.tournament_id]
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
					await self.channel_layer.group_discard(self.tournament_id, self.room['admin']['consumer'].channel_name)
					await self.room['admin']['consumer'].close()
					return
				else:
					await asyncio.sleep(1)
		except Exception as e:
			logger.error(f"Error closing admin connection: {e}")

	async def tournament_end(self):
		logger.debug("tournament_end")
		await self.disconnect_all_users()
		await self.disconnect_admin()
		tournament_manager.remove_room(self.tournament_id)

	# RECEIVE

	async def receive(self, text_data):
		if not self.room:
			return
		try:
			data = json.loads(text_data)
			data_type = data['type']
			tournament_room = self.room['tournament_instance']
			if tournament_room:
				if data_type == 'move' and self.username in self.room['players']:
					tournament_room.input_players(self.username, data['input'])
				elif data_type == 'ready':
					if self.username in self.room['players']:
						async with TournamentConsumer.ready_queue:
							await self.tournament_start()
					elif self.username in self.room['spectator']:
						await self.tournament_start_spectator()
		except json.JSONDecodeError:
			logger.error("Failed to decode JSON data")
		except Exception as e:
			logger.error(f"Unexpected error: {e}")

	async def tournament_start(self):
		self.ready = True
		for player in self.room['players']:
			playerConsumer = self.room['players'][player]['consumer']
			if playerConsumer.ready == False:
				return
		if self.room['status'] == 'loading':
			tournament_manager.update_status('running', self.tournament_id)
			admin = self.room['admin']
			await self.send_tournament_status(admin['id'], None, 'in_progress')
			await self.channel_layer.group_send(self.tournament_id, {
				'type': 'send_state',
				'state': {
					'type': 'tournament_start'
				}
			})
			asyncio.create_task(self.tournament_loop(self.tournament_id))
			logger.debug(f'tournament start')
	
	async def tournament_start_spectator(self):
		self.ready = True
		if self.room['status'] == 'running':
			await self.channel_layer.group_add(self.tournament_id, self.channel_name)
			await self.send_message({
				'type': 'tournament_start'
			})
			logger.debug(f'Spectate start for {self.username}')



	# tournament LOOP

	async def tournament_loop(self, tournament_id):
		if not self.room:
			return
		while tournament_manager.get_room(self.tournament_id):
			tournament = self.room['tournament_instance']
			if tournament:
				tournament_state = await tournament.update()
				await self.channel_layer.group_send(
					tournament_id,
					{
						'type': 'send_state',
						'state': tournament_state
					}
				)
				for team in tournament_state['teams']:
					await self.send_update_score(team['name'], team['level'] * - 1)
				if tournament_state['type'] == 'tournament_end':
					tournament_manager.update_status('finished', self.tournament_id)
					await self.send_tournament_finished(tournament_state['team']['name'], tournament_state['score'] * -1)
					#await self.tournament_end()
					return
				await asyncio.sleep(3)
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
		
	async def send_tournament_finished(self, team, score):
		admin = self.room['admin']
		admin['consumer'].can_be_disconnected = False
		logger.debug(f"{team}: {score}")
		await self.channel_layer.group_send(admin['id'], {
				'type': "send_state",
				'state': {
					'type': "export_status",
					'status': 'finished',
					'team': team,
					'score': score
				}
			})

	# STATUS_LOOP
	async def status_loop(self):
		while self.room['status'] != 'aborted':
			await asyncio.sleep(1)
		await self.tournament_end()

	# UTILS

	async def send_export_data(self, tournament_id, data):
		await self.channel_layer.group_send(tournament_id, {
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

	async def send_tournament_status(self, admin_id, tournament_id, status):
		logger.debug(f"export status {status}")
		groups = []
		if admin_id:
			groups.append(admin_id)
		if tournament_id:
			groups.append(tournament_id)
		await self.send_to_multiple_groups(groups, {
				'type': 'export_status',
				'status': status
		})


	async def send_to_multiple_groups(self, groups, message):
		for group in groups:
			if group:  # S'assurer que le nom du groupe est valide
				try:
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
					event['state']['username'] = self.username
					event['state']['nickname'] = self.nickname
				event['state']['game_private_id'] = self.game_private_id
				await self.send(text_data=json.dumps(event['state']))
				self.can_be_disconnected = True
			else:
				logger.debug(f"{self.username} consumer want send new statde but is closed")
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send state: {e}")
		self.game_private_id = None

