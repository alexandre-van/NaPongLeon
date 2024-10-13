import random
import uuid

MAX_FOOD = 1000  # Augmenté pour une carte plus grande
MAP_WIDTH = 20000
MAP_HEIGHT = 20000

class GameState:
    def __init__(self):
        self.players = {}
        self.food = []
        self.next_player_id = 1
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT
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
            'size': 20,  # Taille initiale
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
            self.players[player_id]['size'] = int(self.players[player_id]['size'])
            self.players[player_id]['score'] = int(self.players[player_id]['score'])

    def add_food(self):
        if len(self.food) < MAX_FOOD:
            attempts = 0
            max_attempts = 50
            min_distance = 10  # Distance minimale entre les éléments de nourriture

            while attempts < max_attempts:
                new_food = {
                    'id': str(uuid.uuid4()),
                    'x': random.randint(0, self.map_width),
                    'y': random.randint(0, self.map_height),
                    'value': 1,
                    'color': f'#{random.randint(0, 0xFFFFFF):06x}'
                }
                # Vérifier la distance avec la nourriture existante
                if all(self.distance(new_food, f) >= min_distance for f in self.food):
                    self.food.append(new_food)
                    break
                attempts += 1
            if attempts == max_attempts:
                print("Impossible de placer de la nourriture après plusieurs tentatives")

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
                player['score'] += food['value']
                self.add_food()  # Ajouter une nouvelle nourriture immédiatement
                return True
        return False

    def distance(self, obj1, obj2):
        return ((obj1['x'] - obj2['x']) ** 2 + (obj1['y'] - obj2['y']) ** 2) ** 0.5

    def initialize_food(self):
        for _ in range(MAX_FOOD):
            self.add_food()

game_state = GameState()
