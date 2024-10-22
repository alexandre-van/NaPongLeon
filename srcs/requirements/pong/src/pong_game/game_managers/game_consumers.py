from ..utils.logger import logger
import json
import asyncio
from .game_manager import game_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from ..utils.decorators import auth_required

class GameConsumer(AsyncWebsocketConsumer):
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
			self.new_users()
		else:
			logger.debug(f'{self.game_id} does not exist')
			await self.send(text_data=json.dumps({
				'error': '404',
				'message': f'{self.game_id} does not exist'
			}))

	async def new_users(self):
		self.ready = False
		if self.admin_id:
			self.room = game_manager.add_admin(self.admin_id, self, self.game_id)
			if self.room is None:
				return
			await self.accept()
			logger.debug(f"Admin is connected !")
		else:
			self.room = game_manager.add_user(self.username, self, self.game_id)
			if self.room is None:
				return
			self.send_user_connection()
			await self.accept()
		if self.room and self.room['status'] == 'startup' and self.room['game_instance'] \
			and self.username in self.room['players']:
			self.startup()
		elif self.room and self.room['status'] != 'waiting' and self.room['game_instance']:
			self.add_user()
		else:
			await self.send_message({
				'type': 'waiting_room',
			})

	async def startup(self):
		self.room.update_status('loading')
		admin = self.room['admin']
		await self.channel_layer.group_add(admin['id'], admin['consumer'].channel_name)
		for player in self.room['players']:
			await self.channel_layer.group_add(self.game_id, self.room['players'][player].channel_name)
		for spectator in self.room['spectator']:
			await self.channel_layer.group_add(self.game_id, self.room['spectator'][spectator].channel_name)
		await self.send_export_data(self.game_id, self.room['game_instance'].export_data())
		logger.debug(f'Export data')
		await self.send_game_status(admin['id'], self.game_id, 'loading')

	async def add_user(self):
		admin = self.room['admin']
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
		else
			return
		groups = [admin_id, self.game_id]
		await self.send_to_multiple_groups(groups, {
				'type': type_name
				'username': self.username
		})

	# DISCONNECT

	async def disconnect(self, close_code): # a clean
		if not self.room:
			return
		self.is_closed = True
		if self.username in self.room['players'] \
			or self.admin_id == self.room['admin']['id']:
			await self.channel_layer.group_discard(self.game_id, self.channel_name)
			for player in self.room['players']:
				try:
					self.room['players'][player].is_closed = True
					await self.room['players'][player].close()
				except Exception as e:
					logger.error(f"Error closing player connection: {e}")
			for spectator in self.room['spectator']:
				try:
					self.room['spectator'][spectator].is_closed = True
					await self.room['spectator'][spectator].close()
				except Exception as e:
					logger.error(f"Error closing spectator connection: {e}")
			try:
				self.room['admin']['consumer'].is_closed = True
				await self.room['admin']['consumer'].close()
			except Exception as e:
				logger.error(f"Error closing admin connection: {e}")

			game_manager.remove_room(self.game_id)
		else:
			if self.username in self.room['spectator']:
				game_manager.remove_user(self.username, self.game_id)

	# RECEIVE

	async def receive(self, text_data):
		if not self.room:
			return
		if self.username not in self.room['players']:
			return
		data = json.loads(text_data)
		game_id = self.game_id
		data_type = data['type']
		game_room = self.room['game_instance']
		if game_room:
			if data_type == 'move' and self.username in self.room['players']:
				game_room.input_players(self.username, data['input'])
			elif data_type == 'ready':
				if self.username in self.room['players']
	
	async def game_start()
		self.ready = True
		for player in self.room['players']
			if self.room['players'][player].ready == False
				return
		if self.room['status'] == 'loading':
			self.room.update_status('running')
			await self.send_game_status(admin_id, None, 'in_process')
			await self.channel_layer.group_send( game_id, {
				'type': 'send_state',
				'state': {
					'type': 'game_start'
				}
			})
			asyncio.create_task(self.game_loop(game_id))
			logger.debug(f'Game start')



	# GAME LOOP

	async def game_loop(self, game_id):
		if not self.room:
			return
		while True:
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
				await asyncio.sleep(0.025)
			else:
				break

	# UTILS

	async def send_export_data(self, game_id, data):
		await self.channel_layer.group_send(game_id, {
				'type': "send_state",
				'state': {
					'type': "export_data",
					'data': data
				}
			})

	async def send_game_status(self, admin_id, game_id, status):
		groups = []
		if admin_id:
			groups.append(admin_id)
		if game_id:
			groups.append(game_id)
		await self.send_to_multiple_groups(groups, {
				'type': 'export_status'
				'status': status
		})

	async def send_to_multiple_groups(self, groups, message):
 		channel_layer = get_channel_layer()
		for group in groups:
			await channel_layer.group_send(
				group, {
					'type': 'send_state',
					'message': message
				}
			)

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
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send state: {e}")

