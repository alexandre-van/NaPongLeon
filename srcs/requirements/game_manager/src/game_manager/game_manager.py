from .models import Player, GameInstance
from .utils.logger import logger
from .private_room.private_room import PrivateRoom, GenerateUsername

class Game_manager:
	game_manager_instance = None

	def __init__(self):
		self.update_databases()
		self.private_rooms = {}
		self.username_generator = GenerateUsername()

	def update_databases(self):
		games_instance = GameInstance.objects.all()
		players = Player.objects.all()
		if players:
			for player in players:
				if player.status != 'inactive':
					player.update_status('inactive')
			for game_instance in games_instance:
				if game_instance.status != 'finished'\
					and  game_instance.status != 'aborted':
					game_instance.abort_game()

	def generate_username(self):
		logger.debug("generate new username")
		return self.username_generator.generate()

	def add_private_room(self, username):
		self.private_rooms[username] = PrivateRoom(username)
		return self.private_rooms[username]

def create_game_manager_instance():
	if Game_manager.game_manager_instance is None:
		logger.debug("creating game manager...")
		Game_manager.game_manager_instance = Game_manager()
		logger.debug("game manager created !")