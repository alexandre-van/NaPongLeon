from ..utils.logger import logger
import json
import asyncio
from .game_manager import game_manager
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
		player_1 = self
		player_1.ready = False
		game_id, player_2 = game_manager.add_player(self)
		player_1.game_id = None
		if game_id:
			player_1.game_id = game_id
			player_2.game_id = game_id
			logger.debug(f'Player connected to game {game_id}')
			await self.channel_layer.group_add(game_id, player_1.channel_name)
			await self.channel_layer.group_add(game_id, player_2.channel_name)
			game_room = game_manager.get_game_room(game_id)
			await self.channel_layer.group_send(game_id, {
				'type': "send_state",
				'state': {	
					'type': "export_data",
					'game_id': game_id,
					'data': game_room.export_data()
				}
			})
			logger.debug(f'Export data')
			asyncio.create_task(player_1.game_loop(game_id))
			asyncio.create_task(player_2.game_loop(game_id))
		else:
			await player_1.send(text_data=json.dumps({'type': 'waiting_room'}))

	async def disconnect(self, close_code):
		player_1 = self
		game_id = player_1.game_id
		if game_id:
			game_room = game_manager.get_game_room(game_id)
			if game_room:
				player_2 = game_room.getopponent(player_1)
				await self.channel_layer.group_discard(game_id, self.channel_name)
				if player_2:
					await player_2.send(text_data=json.dumps({
						'type': 'game_end',
						'reason': 'player_2_disconnected'
					}))
					await player_2.close()
				game_manager.remove_game_roon(game_id)
		else:
			game_manager.remove_player(player_1)

	async def receive(self, text_data):
		player_1 = self
		data = json.loads(text_data)
		game_id = self.game_id
		data_type = data['type']
		game_room = game_manager.get_game_room(game_id)
		if game_room:
			if data_type == 'move':
				game_room.input_players(self, data['input'])
			elif data_type == 'ready':
				player_1.ready = True
				player_2 = game_room.getopponent(player_1)
				if player_2.ready == True:
					await self.channel_layer.group_send( game_id, {
							'type': 'send_state',
							'state': {
								'type': 'game_start'
							}
					})
					logger.debug(f'Game start')
				

	async def game_loop(self, game_id):
		while True:
			game = game_manager.get_game_room(game_id)
			if game:
				game_state = game.update()
				await self.channel_layer.group_send(
					game_id,
					{
						'type': 'send_state',
						'state': game_state
					}
				)
				await asyncio.sleep(0.05)
			else:
				break

	async def send_state(self, event):
		await self.send(text_data=json.dumps(event['state']))
