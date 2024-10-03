import asyncio
import threading
from django.conf import settings
from .matchmaking import Matchmaking

matchmaking_instance = None

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start_matchmaking():
    if not settings.DEBUG:  # Evite de lancer en double en mode de développement
        loop = asyncio.new_event_loop()
        matchmaking_instance = Matchmaking()
        loop.create_task(matchmaking_instance.start_matchmaking_loop())
        
        t = threading.Thread(target=run_async_loop, args=(loop,))
        t.start()