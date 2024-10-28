from ..utils.logger import logger
import json
import asyncio
from ..game_manager import Game_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from ..utils.decorators import auth_required_ws

class PrivateRoomConsumer(AsyncWebsocketConsumer):
	@auth_required_ws
	async def connect(self, username=None):
		self.username = username
		if not self.username:
			self.username = 'Random'
		logger.debug(f"{self.username} tries to connect")
		return

	async def disconnect(self, close_code):
		logger.debug(f"{self.username} is disconnected")
		return
	
	async def receive(self, text_data):
		data = json.loads(text_data)
		logger.debug(f"{self.username} send message : {data}")
		return