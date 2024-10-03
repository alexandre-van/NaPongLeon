from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
import asyncio

class Matchmaking:
    def __init__(self):
        self.is_running = False

    async def start_matchmaking_loop(self):
        self.is_running = True
        while self.is_running:
            print("Matchmaking loop running...")
            await asyncio.sleep(5)  # Simule un travail asynchrone

    def stop_matchmaking(self):
        self.is_running = False