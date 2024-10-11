import random
import uuid

class GameState:
    def __init__(self):
        self.players = {}
        self.food = []
        self.next_player_id = 1

    def generate_player_id(self):
        return str(uuid.uuid4())

    def add_player(self, name):
        player_id = self.generate_player_id()
        self.players[player_id] = {
            'id': player_id,
            'name': name,
            'x': random.randint(0, 1000),
            'y': random.randint(0, 600),
            'size': 10,
            'color': f'#{random.randint(0, 0xFFFFFF):06x}'
        }
        return player_id

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]

    def update_player(self, player_id, x, y):
        if player_id in self.players:
            self.players[player_id]['x'] = x
            self.players[player_id]['y'] = y

    def add_food(self):
        self.food.append({
            'x': random.randint(0, 600),
            'y': random.randint(0, 600),
            'value': 1
        })

    def get_state(self):
        return {
            'players': self.players,
            'food': self.food
        }

game_state = GameState()
