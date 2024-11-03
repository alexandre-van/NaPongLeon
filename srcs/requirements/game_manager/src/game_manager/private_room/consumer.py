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
		self.username = Game_manager.game_manager_instance.generate_username() # developement
		if not self.username:
			logger.debug(f"unregister detected")
			return
		logger.debug(f"{self.username} is connected")
		self.room = Game_manager.game_manager_instance.add_private_room(username)
		if not self.room:
			logger.debug(f"{self.username} private room failed")
			return
		await self.accept()
		return

	async def disconnect(self, close_code):
		if self.username:
			logger.debug(f"{self.username} is disconnected")
		return
	
	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			data_type = data.get('type')
			if data_type:
				if data_type == "choice_game_mode":
					game_mode = data['game_mode']
					self.room.choice_game_mode(game_mode)
				elif data_type == "add_ia_to_team":
					team = data['team']
					self.room.add_ia_to_team(team)
				elif data_type == "remove_ia_to_team":
					team = data['team']
					self.room.remove_ia_to_team(team)
				elif data_type == "start_game":
					self.room.start_game()
				else:
					logger.warning(f"{self.username} : No handler found for message type: {data_type}")
			else:
				logger.warning(f"{self.username} : No message type found for message")
		except json.JSONDecodeError:
			logger.error("Failed to decode JSON data")
		except Exception as e:
			logger.error(f"Unexpected error: {e}")