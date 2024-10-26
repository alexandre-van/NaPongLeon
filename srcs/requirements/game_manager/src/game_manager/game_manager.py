from .models import Player, GameInstance
from .utils.logger import logger

class Game_manager:
	game_manager_instance = None

	def __init__(self):
		self.update_databases()
	
	def update_databases(self):
		games_instance = GameInstance.objects.all()
		players = Player.objects.all()
		for player in players:
			if player.status != 'inactive':
				player.update_status('inactive')
		for game_instance in games_instance:
			if game_instance.status != 'finished'\
				and  game_instance.status != 'aborted':
				game_instance.abort_game()

def create_game_manager_instance():
	if Game_manager.game_manager_instance is None:
		Game_manager.game_manager_instance = Game_manager()