
class Team:
    def __init__(self, players):
        self.players = players
        self.score = 0
        self.team_name = ", ".join(players)