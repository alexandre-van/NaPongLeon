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
		self.game_id = None
		if len(segments) >= 4:
			self.game_id = segments[3]
		self.username = username
		logger.debug(f'{self.username} tries to connect to the game: {self.game_id}')
		if game_manager.get_room(self.game_id) is not None:
			await self.accept()
			self.ready = False
			self.room = game_manager.add_player(self.username, self, self.game_id)
			if self.room is not None:
				logger.debug(f"{username} is in waiting room !")
			if self.room['game_instance']:
				for player in self.room['players']:
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
		player_1 = self
		game_id = player_1.game_id
		if game_id:
			game_room = self.room['game_instance']
			if game_room:
				player_2 = game_room.getopponent(player_1)
				await self.channel_layer.group_discard(game_id, self.channel_name)
				if player_2:
					await player_2.send(text_data=json.dumps({
						'type': 'game_end',
						'reason': 'player_2_disconnected'
					}))
					await player_2.close()
				game_manager.remove_room(game_id)
		else:
			game_manager.remove_player(player_1)

	async def receive(self, text_data):
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
		await self.send(text_data=json.dumps(event['state']))
