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
		self.is_closed = False
		self.can_be_disconnected = True
		if not self.username:
			logger.debug(f"unregister detected")
			return
		logger.debug(f"{self.username} is connected")
		self.room = Game_manager.game_manager_instance.add_private_room(self.username)
		if not self.room:
			logger.debug(f"{self.username} private room failed")
			return
		await self.accept()
		await self.channel_layer.group_add(self.username, self.channel_name)
		return

	async def disconnect(self, close_code):
		if self.username:
			logger.debug(f"{self.username} is disconnected")
		return
	
	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			data_type = data.get('type')
			state = None
			if data_type:
				if data_type == "choice_game_mode":
					game_mode = data['game_mode']
					state = self.room.choice_game_mode(game_mode)
				elif data_type == "add_AI_to_team":
					team = data['team']
					state = self.room.add_AI_to_team(team)
				elif data_type == "remove_user_or_AI":
					id = data['ID']
					state = self.room.remove_user_or_AI(id)
				elif data_type == "start_game":
					state = self.room.start_game()
				else:
					logger.warning(f"{self.username} : No handler found for message type: {data_type}")
				logger.debug(f"state : {state}")
				await self.channel_layer.group_send(self.username, {
					'type': 'send_state',
					'state': state
				})
			else:
				logger.warning(f"{self.username} : No message type found for message")
		except json.JSONDecodeError:
			logger.error("Failed to decode JSON data")
		except Exception as e:
			logger.error(f"Unexpected error: {e}")

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