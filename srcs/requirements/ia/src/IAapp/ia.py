# ia.py
import json

class IA:
    def __init__(self):
        # Initialisation de votre IA
        print("IA instantiated.")

    def on_message(self, ws, message):
        data = json.loads(message)
        print("Message reçu:", data)

        # Vérifiez le type de message et agissez en conséquence
        if data['type'] == 'waiting_room':
            print("En attente d'un adversaire...")
        elif data['type'] == 'export_data':
            game_id = data['game_id']
            print("Jeu créé! ID du jeu :", game_id)
            # Ici, vous pourriez appeler une méthode pour initialiser le jeu
        elif data['type'] == 'game_start':
            print("Le jeu a commencé!")
            # Commencez votre logique de jeu ici
        elif data['type'] == 'gu':
            # Mettez à jour l'état du jeu
            print("État du jeu mis à jour:", data)
        elif data['type'] == 'scored':
            print(data['msg'])
        elif data['type'] == 'game_end':
            print("Jeu terminé. Raison:", data['reason'])
            ws.close()

    def on_error(self, ws, error):
        print("Erreur:", error)

    def on_close(self, ws):
        print("Connexion WebSocket fermée.")

    def on_open(self, ws):
        print("Connexion WebSocket établie.")
