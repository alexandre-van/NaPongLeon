from django.apps import AppConfig

class game_managerConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'game_manager'

	def ready(self):
		from .game_manager import create_game_manager_instance
		create_game_manager_instance()