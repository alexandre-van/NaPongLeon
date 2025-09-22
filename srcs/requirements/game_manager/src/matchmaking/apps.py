from django.apps import AppConfig
from game_manager.utils.logger import logger

class MatchmakingConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'matchmaking'
	def ready(self):
		from .thread import start_matchmaking, stop_matchmaking
		from game_manager.utils.logger import logger
		import atexit
		logger.debug("starting matchmaking...")
		start_matchmaking()
		atexit.register(stop_matchmaking)
