from game_manager.utils.logger import logger
from .game_manager import Game_manager
import asyncio
import threading

game_manager_thread = None

class AsyncLoopThread(threading.Thread):
	def __init__(self, loop):
		logger.debug("Initializing game_manager thread...")
		threading.Thread.__init__(self, daemon=True)
		self.loop = loop

	def run(self):
		logger.debug("Starting game_manager thread...")
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

	def stop(self):
		logger.debug("Stopping game_manager thread...")
		if self.loop.is_running():
			self.loop.call_soon_threadsafe(self.loop.stop)
			self.join()

def start_game_manager():
	global game_manager_thread
	if game_manager_thread is None:
		logger.debug("Starting game_manager service...")
	
		game_manager_instance = Game_manager.game_manager_instance
		loop = asyncio.new_event_loop()
		loop.create_task(game_manager_instance.start_game_manager_loop())

		game_manager_thread = AsyncLoopThread(loop)
		game_manager_thread.start()

def stop_game_manager():
	global game_manager_thread
	if game_manager_thread:
		logger.debug("Stopping game_manager service...")
		game_manager_instance = Game_manager.game_manager_instance
		
		if game_manager_instance:
			game_manager_instance.stop_game_manager()
			
		game_manager_thread.stop()
		game_manager_thread = None
		game_manager_instance = None

		logger.debug("Game_manager service stopped.")

