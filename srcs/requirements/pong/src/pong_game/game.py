import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongGame:
    def __init__(self, player1, player2):
        self.players = [player1, player2]