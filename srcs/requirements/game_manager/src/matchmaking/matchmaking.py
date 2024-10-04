from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
import asyncio
import threading

class Matchmaking:
	def __init__(self):
		logger.debug("Matchmaking init...")
		self._is_running = False
		self._task = None
		self.mutex = threading.Lock()

	async def start_matchmaking_loop(self):
		with self.mutex:
			self._is_running = True

		self._task = asyncio.current_task()
		try:
			while True:
				with self.mutex:
					if not self._is_running:
						break
				logger.debug("Matchmaking loop is running...")
				await asyncio.sleep(1)
			logger.debug("Matchmaking stopped.")
		except asyncio.CancelledError:
			logger.debug("Matchmaking loop has been cancelled.")
		finally:
			logger.debug("Exiting matchmaking loop.")

	def stop_matchmaking(self):
		logger.debug("Matchmaking stopping...")
		with self.mutex:
			self._is_running = False
			if self._task:
				self._task.cancel()
