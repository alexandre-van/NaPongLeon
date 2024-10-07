from ..game.game import Game
from ..utils.logger import logger
import uuid

class game_manager:
	def __init__(self) :
		self.games_room = {}
		self.waiting_room = []
		logger.debug("\ngame_manager initialised\n")

	def add_player(self, player_1):
		if len(self.waiting_room) == 0:
			logger.debug("\nPlayer in waiting room\n")
			self.waiting_room.append(player_1)
			return None, None
		else:
			player_2 = self.waiting_room.pop(0)
			game_id = str(uuid.uuid4())
			new_game = Game(player_1, player_2)
			self.games_room[game_id] = new_game
			return game_id, player_2

	def remove_player(self, player_1):
		if player_1 in self.waiting_room:
			self.waiting_room.remove(player_1)

	def remove_game_roon(self, game_id):
		if self.games_room.get(game_id):
			del game_manager.games_room[game_id]

	def get_game_room(self, game_id):
		return self.games_room.get(game_id)


game_manager = game_manager()
