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
		if len(segments) >= 4:
			self.game_id = segments[3]
		if len(segments) >= 6:
			self.admin_id = segments[4]
			logger.debug(f'admin_id = {self.admin_id}')
			self.username = 'admin'
		if not self.username and not self.admin_id:
			logger.warning(f'An unauthorized connection has been received')
			return
		logger.debug(f'{self.username} tries to connect to the game: {self.game_id}')
		if game_manager.get_room(self.game_id) is not None:
			await self.new_users()
		else:
			logger.debug(f'{self.game_id} does not exist')
			await self.send(text_data=json.dumps({
				'error': '404',
				'message': f'{self.game_id} does not exist'
			}))

	async def new_users(self):
		logger.debug("new_user")
		self.ready = False
		if self.admin_id:
			self.room = game_manager.add_admin(self.admin_id, self, self.game_id)
			if self.room is None:
				return
			await self.accept()
			await self.channel_layer.group_add(self.admin_id, self.channel_name)
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
		elif self.room and self.room['status'] != 'waiting' and self.room['game_instance']:
			await self.add_user()
		else:
			await self.send_message({
				'type': 'waiting_room',
			})

	async def startup(self):
		logger.debug("startup")
		game_manager.update_status('loading', self.game_id)
		admin = self.room['admin']
		for player in self.room['players']:
			await self.channel_layer.group_add(self.game_id, self.room['players'][player].channel_name)
		for spectator in self.room['spectator']:
			await self.channel_layer.group_add(self.game_id, self.room['spectator'][spectator].channel_name)
		await self.send_game_status(admin['id'], self.game_id, 'loading')
		game_data = self.room['game_instance'].export_data()
		await self.send_export_teams(admin['id'], game_data['teams'])
		await self.send_export_data(self.game_id, game_data)
		logger.debug(f'Export data')

	async def add_user(self):
		await self.send_message({
			'type': "export_data",
			'data': self.room['game_instance'].export_data()
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
			await self.game_end()
			return
		if self.username in self.room['players']:
			admin = self.room['admin']
			await self.send_game_status(admin['id'], self.game_id, 'aborted')
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
		if self.username not in self.room['players']:
			return
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
					await self.send_game_finished(game_state['team'], game_state['score'])
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
		
	async def send_game_finished(self, team, score):
		admin = self.room['admin']
		admin['consumer'].can_be_disconnected = False
		await self.channel_layer.group_send(admin['id'], {
				'type': "send_state",
				'state': {
					'type': "export_status",
					'status': 'finished',
					'team': team,
					'score': score
				}
			})

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
					logger.debug(f"Sending message to group: {group}")
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
				await self.send(text_data=json.dumps(event['state']))
				self.can_be_disconnected = True
			else:
				logger.debug(f"{self.username} consumer want send new statde but is closed")
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send state: {e}")

