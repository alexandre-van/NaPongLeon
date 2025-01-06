from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game_manager.game_manager import Game_manager
from game_manager.utils.logger import logger
from .matchmaking import Matchmaking
from game_manager.utils.decorators import auth_required_ws
import uuid

class MatchmakingConsumer(AsyncJsonWebsocketConsumer):
	@auth_required_ws
	async def connect(self, username=None, nickname=None):
		logger.debug("hello")
		self.closed = False
		self.username = username
		self.nickname = nickname
		if self.username:
			await self.accept()
			await Game_manager.game_manager_instance.create_new_player_instance(self.username)
		else:
			logger.warning(f'An unauthorized connection has been received')

	async def disconnect(self, close_code):
		self.closed = True
		try:
			status = await Game_manager.game_manager_instance.get_player_status(self.username)
			if status == 'in_queue':
				await Matchmaking.matchmaking_instance.remove_player_request(self.username)
				await Game_manager.game_manager_instance.update_player_status(self.username, 'inactive')
		except Exception as e:
			logger.error(f"Error in disconnect: {str(e)}")

	async def receive_json(self, content):
		try:
			action = content.get('action')
			if action == 'join_matchmaking':
				await self.handle_join_matchmaking(content)
			elif action == 'leave_matchmaking':
				await self.handle_leave_matchmaking()
			else:
				logger.debug(content)
				
		except Exception as e:
			logger.error(f"Error processing message: {str(e)}")
			await self.send_json({
				'status': 'error',
				'message': 'Internal server error'
			})

	async def handle_join_matchmaking(self, data):
		game_mode = data.get('game_mode')
		modifiers = data.get('modifiers', '')
		number_of_players = data.get('number_of_players', '')
		
		if not game_mode or game_mode not in Matchmaking.matchmaking_instance.GAME_MODES:
			await self.send_json({
				'status': 'error',
				'message': 'Invalid game mode'
			})
			return
			
		modifier_list = Game_manager.game_manager_instance.check_modifier(modifiers, game_mode)
		if modifier_list is None:
			await self.send_json({
				'status': 'error',
				'message': 'Invalid modifiers'
			})
			return
			
		try:
			await Matchmaking.matchmaking_instance.add_player_request(
				self.username, 
				game_mode, 
				modifier_list, 
				number_of_players,
				self
			)
		except Exception as e:
			logger.error(f"Error joining matchmaking: {str(e)}")
			await self.send_json({
				'status': 'error',
				'message': 'Failed to join matchmaking'
			})

	async def handle_leave_matchmaking(self):
		try:
			await Matchmaking.matchmaking_instance.remove_player_request(self.username)
			await self.send_json({
				'status': 'success',
				'message': 'Left matchmaking queue'
			})
		except Exception as e:
			logger.error(f"Error leaving matchmaking: {str(e)}")
			await self.send_json({
				'status': 'error',
				'message': 'Failed to leave matchmaking'
			})