from django.apps import AppConfig

class game_managerConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'game_manager'

	def ready(self):
		from .game_manager import create_game_manager_instance
		from .thread import start_game_manager, stop_game_manager
		from .utils.logger import logger
		import atexit
		create_game_manager_instance()
		logger.debug("starting game_manager...")
		start_game_manager()
		atexit.register(stop_game_manager)
