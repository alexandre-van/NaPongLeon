import json
from .game_manager import GameManager
from channels.generic.websocket import AsyncWebsocketConsumer


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        game_id = GameManager.add_player(self)
        if game_id:
            await self.channel_layer.group_add(game_id, self.channel_name)
            await self.send(text_data=json.dumps({'type': 'game_start', 'game_id': game_id}))

    async def disconnect(self, close_code):
        GameManager.remove_player(self)
        # Nettoyer les groupes et les parties

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'move':
            game = GameManager.get_game(data['game_id'])
            if game:
                game_state = game.update(self, data['position'])
                await self.channel_layer.group_send(
                    data['game_id'],
                    {'type': 'game_update', 'state': game_state}
                )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['state']))