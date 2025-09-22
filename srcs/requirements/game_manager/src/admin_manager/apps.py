from django.apps import AppConfig
from game_manager.utils.logger import logger

class admin_managerConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'admin_manager'
	def ready(self):
		from .admin_manager import AdminManager
		from game_manager.utils.logger import logger
		import atexit
		logger.debug("set admin_manager atexit...")
		atexit.register(AdminManager.admin_manager_instance.close_all)
