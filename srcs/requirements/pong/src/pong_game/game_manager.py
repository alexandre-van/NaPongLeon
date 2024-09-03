import uuid
from .game import PongGame

class GameManager:
    def __init__(self) :
        self.games_room = {}
        self.waiting_room = []

    def add_player(self, player):
        if len(self.waiting_room) == 0:
            self.waiting_room.append(player)
            return None
        else:
            opponent = self.waiting_room.pop(0)
            game_id = str(uuid.uuid4())
            new_game = PongGame(player, opponent)
            self.games_room[game_id] = new_game
            return game_id

    def remove_player(self, player):
        if player in self.waiting_room:
            self.waiting_room.remove(player)
            # Gérer le cas où le joueur est dans une partie en cours

    def get_game(self, game_id):
        return self.games_room.get(game_id)