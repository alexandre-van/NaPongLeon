import sys
from game_manager.utils.logger import logger
from django.conf import settings
from .matchmaking import Matchmaking
import asyncio
import threading
import atexit
import signal
from .mutex import mutex

matchmaking_thread = None
matchmaking_instance = Matchmaking()
atexit.register(matchmaking_instance.stop_matchmaking)

def signal_handler(signal, frame):
    logger.debug("Received signal to stop, cleaning up...")
    stop_matchmaking()
    sys.exit(0)

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
    global matchmaking_thread, matchmaking_instance
    if matchmaking_thread is None:
        logger.debug("Starting matchmaking service...")
        loop = asyncio.new_event_loop()

        signal.signal(signal.SIGTERM, signal_handler)

        loop.create_task(matchmaking_instance.start_matchmaking_loop())

        matchmaking_thread = AsyncLoopThread(loop)
        matchmaking_thread.start()

def stop_matchmaking():
    global matchmaking_thread, matchmaking_instance
    if matchmaking_thread:
        logger.debug("Stopping matchmaking service...")
        
        # Utiliser le mutex lors de l'accès à matchmaking_instance
        with mutex:
            if matchmaking_instance:
                matchmaking_instance.stop_matchmaking()
            matchmaking_thread.stop()
            matchmaking_thread = None
            matchmaking_instance = None

        logger.debug("Matchmaking service stopped.")
