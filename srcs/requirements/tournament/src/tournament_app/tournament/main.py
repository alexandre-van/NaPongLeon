from tournament import Tournament

def main():
    logger.debug("Hello World !")
    players_test = generatePlayers(256)

    Tournament(players_test, "PONG_CLASSIC", None)

def generatePlayers(n):
    players_test = {}
    i = 1
    while i < n + 1:
        players_test[f"{str(i)}"] = None
        i += 1
    return players_test

main()