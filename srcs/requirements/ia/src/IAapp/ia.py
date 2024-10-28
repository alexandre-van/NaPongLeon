# ia.py
import json
from .logger import logger

class IA:
	def __init__(self):
		self.ball_pos = {'x': 0, 'y': 0, 'z': 1}
		self.previous_ball_pos = None
		self.paddle_pos = {'p1': 0.0, 'p2': 0.0}
		self.is_moving_up = False
		self.is_moving_down = False
		self.ball_velocity = {'x': 0, 'y': 0}
		self.court_height = 52  # Hauteur normalisée du terrain (-26 à 26)
		self.paddle_height = 5 # Hauteur approximative de la raquette
		# Initialisation de votre IA
		logger.debug("IA instantiated.")
  
  
	def calculate_ball_velocity(self):
		"""
		Calcule la vélocité de la balle basée sur ses positions actuelles et précédentes
		"""
		if self.previous_ball_pos is not None:
			self.ball_velocity = {
				'x': self.ball_pos['x'] - self.previous_ball_pos['x'],
				'y': self.ball_pos['y'] - self.previous_ball_pos['y']
			}

	def on_message(self, ws, message):
		data = json.loads(message)
		logger.debug(f"Message reçu: {data}")
			# Vérifiez le type de message et agissez en conséquence
		if data['type'] == 'waiting_room':
			logger.debug("En attente d'un adversaire...")
		elif data['type'] == 'export_data':
			game_id = data['game_id']
			logger.debug("Jeu créé! ID du jeu :", game_id)
			# Ici, vous pourriez appeler une méthode pour initialiser le jeu
		elif data['type'] == 'game_start':
			logger.debug("Le jeu a commencé!")
			# Commencez votre logique de jeu ici
		elif data['type'] == 'gu':
			self.ball_pos = data['bp']
			self.paddle_pos = data['pp']
			self.ft_move(ws)
		elif data['type'] == 'scored':
			logger.debug(data['msg'])
		elif data['type'] == 'game_end':
			logger.debug(f"Jeu terminé. Raison: {data['reason']}")
			ws.close()

	def on_error(self, ws, error):
		logger.debug(f"Erreur: {error}")

	def on_close(self, ws):
		logger.debug("Connexion WebSocket fermée.")

	def on_open(self, ws):
		logger.debug("Connexion WebSocket établie.")
		
	def send_command(self, ws, command):
		"""
		Envoie une commande de mouvement
		1: monter
		2: descendre
		3: arrêter de monter
		4: arrêter de descendre
		"""
		ws.send(json.dumps({
			'type': 'move',
			'input': command
		}))
		logger.debug(f"Commande envoyée: {command}")
		
	def ft_move(self, ws):
		"""
		Déplace la raquette en fonction de la position de la balle
		Gère les commandes de début et fin de mouvement
		"""
		try:
			# Marge de tolérance pour éviter les oscillations
			TOLERANCE = 0.1
			
			# Si la balle est au-dessus de la raquette
			if self.ball_pos['y'] > self.paddle_pos['p1'] + TOLERANCE:
				if not self.is_moving_up:
					if self.is_moving_down:
						self.send_command(ws, 4)  # Arrêter de descendre
						self.is_moving_down = False
					self.send_command(ws, 1)  # Commencer à monter
					self.is_moving_up = True
					logger.debug("MONTE")
			
			# Si la balle est en-dessous de la raquette
			elif self.ball_pos['y'] < self.paddle_pos['p1'] - TOLERANCE:
				if not self.is_moving_down:
					if self.is_moving_up:
						self.send_command(ws, 3)  # Arrêter de monter
						self.is_moving_up = False
					self.send_command(ws, 2)  # Commencer à descendre
					self.is_moving_down = True
					logger.debug("DESCEND")
			
			# Si la balle est au niveau de la raquette
			else:
				if self.is_moving_up:
					self.send_command(ws, 3)  # Arrêter de monter
					self.is_moving_up = False
				elif self.is_moving_down:
					self.send_command(ws, 4)  # Arrêter de descendre
					self.is_moving_down = False
				logger.debug("STABLE")
	
		except Exception as e:
			logger.error(f"Erreur lors du mouvement: {str(e)}")