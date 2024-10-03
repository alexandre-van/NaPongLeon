from django.apps import AppConfig
from game_manager.utils.logger import logger

class MatchmakingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matchmaking'

    def ready(self):
        from .signals import start_matchmaking
        logger.debug("Ready...\n")
        start_matchmaking()