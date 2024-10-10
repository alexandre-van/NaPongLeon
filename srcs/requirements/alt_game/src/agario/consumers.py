import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_state import game_state
from asgiref.sync import async_to_sync

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.player_id = game_state.add_player(f"Player_{self.channel_name}")
        await self.channel_layer.group_add("game", self.channel_name)
        await self.send(text_data=json.dumps({
            "yourPlayerId": self.player_id,
            **game_state.get_state()
        }))

    async def disconnect(self, close_code):
        game_state.remove_player(self.player_id)
        await self.channel_layer.group_discard("game", self.channel_name)
        await self.send_game_state_to_group()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'move':
            game_state.update_player(self.player_id, data['x'], data['y'])
        await self.send_game_state_to_group()

    async def send_game_state(self):
        await self.send(text_data=json.dumps(game_state.get_state()))

    async def send_game_state_to_group(self):
        await self.channel_layer.group_send(
            "game",
            {
                "type": "game_state_update",
                "game_state": game_state.get_state()
            }
        )

    async def game_state_update(self, event):
        await self.send(text_data=json.dumps(event["game_state"]))
