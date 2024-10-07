from game_manager.utils.logger import logger
from .matchmaking import Matchmaking
import asyncio
import threading

matchmaking_thread = None

class AsyncLoopThread(threading.Thread):
	def __init__(self, loop):
		logger.debug("Initializing matchmaking thread...")
		threading.Thread.__init__(self, daemon=True)
		self.loop = loop

	def run(self):
		logger.debug("Starting matchmaking thread...")
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

	def stop(self):
		logger.debug("Stopping matchmaking thread...")
		if self.loop.is_running():
			self.loop.call_soon_threadsafe(self.loop.stop)
			self.join()

def start_matchmaking():
	global matchmaking_thread
	if matchmaking_thread is None:
		logger.debug("Starting matchmaking service...")
	
		matchmaking_instance = Matchmaking.matchmaking_instance
		loop = asyncio.new_event_loop()
		loop.create_task(matchmaking_instance.start_matchmaking_loop())

		matchmaking_thread = AsyncLoopThread(loop)
		matchmaking_thread.start()

def stop_matchmaking():
	global matchmaking_thread
	if matchmaking_thread:
		logger.debug("Stopping matchmaking service...")
		matchmaking_instance = Matchmaking.matchmaking_instance
		
		if matchmaking_instance:
			matchmaking_instance.stop_matchmaking()
			
		matchmaking_thread.stop()
		matchmaking_thread = None
		matchmaking_instance = None

		logger.debug("Matchmaking service stopped.")

