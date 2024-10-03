from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
from .mutex import mutex
import asyncio
import threading


class Matchmaking:
	def __init__(self):
		logger.debug("Matchmaking init...")
		self.is_running = False

	async def start_matchmaking_loop(self):
		with mutex:  # Assurer l'accès exclusif à is_running
			self.is_running = True

		try:
			while True:
				with mutex:  # Vérifier l'état d'exécution à chaque itération
					if not self.is_running:
						break
				logger.debug("Matchmaking loop is running...")
				await asyncio.sleep(1)
		except asyncio.CancelledError:
			logger.debug("Matchmaking loop has been cancelled.")
		finally:
			logger.debug("Exiting matchmaking loop.")

	def stop_matchmaking(self):
		logger.debug("Matchmaking stopping...")
		with mutex:  # Protéger l'accès à is_running
			self.is_running = False
