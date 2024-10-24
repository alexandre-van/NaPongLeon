from django.apps import AppConfig


class game_managerConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'game_manager'
	def ready(self):
		from django.core.signals import request_started
		from django.dispatch import receiver
		from .game_manager import create_game_manager_instance
		from game_manager.utils.logger import logger
		
		@receiver(request_started)
		def start(sender, **kwargs):
			logger.debug("creating game manager...")
			create_game_manager_instance()
			logger.debug("game manager created !")
