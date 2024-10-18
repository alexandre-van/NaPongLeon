from ..utils.logger import logger
import json
import asyncio
from .game_manager import game_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from ..utils.decorators import auth_required

class GameConsumer(AsyncWebsocketConsumer):
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
			return
		logger.debug(f'{self.username} tries to connect to the game: {self.game_id}')
		if game_manager.get_room(self.game_id) is not None:
			await self.accept()
			self.ready = False
			if self.admin_id:
				self.room = game_manager.add_admin(self.admin_id, self, self.game_id)
				if self.room is not None:
					logger.debug(f"admin is in waiting room !")
			else:
				self.room = game_manager.add_user(self.username, self, self.game_id)
				if self.room is not None:
					logger.debug(f"{username} is in waiting room !")
			if self.room and self.room['game_instance']:
				await self.channel_layer.group_add(self.game_id, self.room['admin']['consumer'].channel_name)
				for player in self.room['players']:
					await self.channel_layer.group_add(self.game_id, self.room['players'][player].channel_name)
				for player in self.room['spectator']:
					await self.channel_layer.group_add(self.game_id, self.room['players'][player].channel_name)
				await self.channel_layer.group_send(self.game_id, {
					'type': "send_state",
					'state': {
						'type': "export_data",
						'data': self.room['game_instance'].export_data()
					}
				})
				logger.debug(f'Export data')
			else:
				await self.send(text_data=json.dumps({'type': 'waiting_room'}))

	async def disconnect(self, close_code):
		if not self.room:
			return
		self.is_closed = True
		if self.username not in self.room['spectator']:
			#await self.channel_layer.group_send(self.game_id, {
			#	'type': "send_state",
			#	'state': {
			#		'type': 'game_end',
			#		'reason': 'player_2_disconnected'
			#	}
			#})
			await self.channel_layer.group_discard(self.game_id, self.channel_name)
			for player in self.room['players']:
				try:
					await self.room['players'][player].close()
				except Exception as e:
					print(f"Error closing player connection: {e}")
			for spectator in self.room['spectator']:
				try:
					await self.room['spectator'][spectator].close()
				except Exception as e:
					print(f"Error closing spectator connection: {e}")
			try:
				await self.room['admin']['consumer'].close()
			except Exception as e:
				print(f"Error closing admin connection: {e}")

			game_manager.remove_room(self.game_id)
		else:
			if self.username in self.room['spectator']:
				game_manager.remove_user(self.username, self.game_id)


	async def receive(self, text_data):
		if not self.room:
			return
		if self.username not in self.room['players']:
			return
		player_1 = self
		data = json.loads(text_data)
		game_id = self.game_id
		data_type = data['type']
		game_room = self.room['game_instance']
		if game_room:
			if data_type == 'move':
				game_room.input_players(self, data['input'])
			elif data_type == 'ready':
				player_1.ready = True
				player_2 = game_room.getopponent(player_1)
				if not game_room.started and player_2.ready:
					game_room.started = True
					await self.channel_layer.group_send( game_id, {
							'type': 'send_state',
							'state': {
								'type': 'game_start'
							}
					})
					asyncio.create_task(player_1.game_loop(game_id))
					asyncio.create_task(player_2.game_loop(game_id))
					logger.debug(f'Game start')


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

	async def send_state(self, event):
		try:
			if self.is_closed is False:
				await self.send(text_data=json.dumps(event['state']))
		except Exception as e:
			logger.warning(f"{self.username}: Failed to send state: {e}")

