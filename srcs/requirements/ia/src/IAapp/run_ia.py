# run_ia.py
from ia import IA
import websocket

def run_ia():
    host = 'localhost'  # Ou l'adresse IP de votre serveur
    port = '8000'       # Changez le port si nécessaire
    websocket_url = f"ws://{host}:{port}/ws/pong/"
    
    ia = IA()

    ws = websocket.WebSocketApp(websocket_url,
                                on_open=ia.on_open,
                                on_message=ia.on_message,
                                on_error=ia.on_error,
                                on_close=ia.on_close)
    
    ws.run_forever()

if __name__ == "__main__":
    run_ia()