from ..utils.logger import logger
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
		player = self
		await player.send(text_data=json.dumps({'type': 'waiting_room'}))

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		pass
				
	async def send_state(self, event):
		await self.send(text_data=json.dumps(event['state']))
