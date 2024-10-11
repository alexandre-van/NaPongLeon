import random
import uuid

MAX_FOOD = 200  # Nombre maximum de nourriture sur la carte

class GameState:
    def __init__(self):
        self.players = {}
        self.food = []
        self.next_player_id = 1
        self.map_width = 2000
        self.map_height = 2000
        self.initialize_food()

    def generate_player_id(self):
        return str(uuid.uuid4())

    def add_player(self, name):
        player_id = self.generate_player_id()
        self.players[player_id] = {
            'id': player_id,
            'name': name,
            'x': random.randint(0, self.map_width),
            'y': random.randint(0, self.map_height),
            'size': 20,  # Augmentation de la taille initiale
            'score': 0,  # Score initial
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
            self.players[player_id]['score'] = self.players[player_id]['size']

    def add_food(self):
        if len(self.food) < MAX_FOOD:
            self.food.append({
                'x': random.randint(0, self.map_width),
                'y': random.randint(0, self.map_height),
                'value': 1
            })

    def get_state(self):
        return {
            'players': self.players,
            'food': self.food
        }

    def check_food_collision(self, player_id):
        player = self.players[player_id]
        for food in self.food[:]:  # Utiliser une copie pour éviter les problèmes de modification pendant l'itération
            if self.distance(player, food) < player['size']:
                self.food.remove(food)
                player['size'] += food['value']
                self.add_food()  # Ajouter une nouvelle nourriture immédiatement
                return True
        return False

    def distance(self, obj1, obj2):
        return ((obj1['x'] - obj2['x']) ** 2 + (obj1['y'] - obj2['y']) ** 2) ** 0.5

    def initialize_food(self):
        for _ in range(MAX_FOOD):
            self.add_food()

game_state = GameState()
