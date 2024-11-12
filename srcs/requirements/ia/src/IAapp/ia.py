# ia.py
import json
import time
from .logger import logger

class IA:
	def __init__(self):
		self.ball_pos = {'x': 0, 'y': 0, 'z': 1}
		self.previous_ball_pos = None
		self.paddle_pos = {'p1': 0.0, 'p2': 0.0}
		self.is_moving_up = False
		self.is_moving_down = False
		self.ball_velocity = {'x': 0, 'y': 0}
		self.predicted_y = 0
		self.optimal_paddle_position = 0

		self.last_message_time = 0
		self.last_message_time2 = 0
		self.message_cooldown = 0.2  # 1 seconde de délai

		# Constantes du terrain
		self.COURT_HEIGHT = 32  # Hauteur du terrain (-30 à 30)
		self.COURT_WIDTH = 42   # Largeur du terrain (-42 à 42)
		self.PADDLE_HEIGHT = 12 # Hauteur de la raquette
		self.PADDLE_MAX_Y = 26  # Position Y maximale de la raquette
		self.PADDLE_MIN_Y = -26 # Position Y minimale de la raquette

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
		logger.debug(f"Vélocité : {self.ball_velocity}")

	def predict_ball_intersection(self):
		"""
		Prédit le point d'intersection de la balle avec le plan de la raquette
		Retourne la position y prédite ou None si la balle s'éloigne
		"""
		if self.ball_velocity['x'] == 0:
			return None

		# Si la balle s'éloigne de notre raquette
		if self.ball_velocity['x'] > 0:
			return None

		# Position x de notre raquette
		paddle_x = -39 # 39 pour la raquette droite et -39 pour gauche

		# Calcul du temps jusqu'à l'intersection
		distance_to_paddle = paddle_x - self.ball_pos['x']
		time_to_intersection = distance_to_paddle / self.ball_velocity['x']

		# Calcul de la position y prédite
		predicted_y = self.ball_pos['y'] + (self.ball_velocity['y'] * time_to_intersection)

		# Prise en compte des rebonds
		bounces = 0
		while abs(predicted_y) > self.COURT_HEIGHT:  # Rebonds sur les murs (30 ou -30)
			if predicted_y > self.COURT_HEIGHT:
				predicted_y = 2 * self.COURT_HEIGHT - predicted_y  # Rebond sur le mur supérieur
			elif predicted_y < -self.COURT_HEIGHT:
				predicted_y = -2 * self.COURT_HEIGHT - predicted_y  # Rebond sur le mur inférieur
			bounces += 1
			if bounces > 10:  # Limite de sécurité pour éviter une boucle infinie
				break

		return predicted_y

	def get_optimal_paddle_position(self, predicted_y):
		"""
		Détermine la position optimale de la raquette en fonction de la prédiction
		"""
		if predicted_y is None:
			return self.paddle_pos['p1']  # Maintenir la position actuelle

		# Ajustement pour centrer la raquette sur le point d'intersection prédit
		half_paddle = self.PADDLE_HEIGHT / 2
		self.optimal_paddle_position = predicted_y - half_paddle

		# Limiter la position aux bornes permises pour la raquette
		self.optimal_paddle_position = max(self.PADDLE_MIN_Y, min(self.PADDLE_MAX_Y, self.optimal_paddle_position))

		return self.optimal_paddle_position

	def ft_move(self, ws, optimal_position):
		"""
		Déplace la raquette de manière prédictive en fonction de la trajectoire calculée
		"""
		try:
			# Marge de tolérance adaptée à l'échelle du terrain
			TOLERANCE = 5  # Augmentée car l'échelle est plus grande

			# Décision de mouvement basée sur la position optimale
			if self.paddle_pos['p1'] + TOLERANCE < optimal_position:
				if not self.is_moving_up:
					if self.is_moving_down:
						self.send_command(ws, 4)  # Arrêter de descendre
						self.is_moving_down = False
					self.send_command(ws, 1)  # Monter
					self.is_moving_up = True
					logger.debug("MONTE vers position optimale")

			elif self.paddle_pos['p1'] - TOLERANCE > optimal_position:
				if not self.is_moving_down:
					if self.is_moving_up:
						self.send_command(ws, 3)  # Arrêter de monter
						self.is_moving_up = False
					self.send_command(ws, 2)  # Descendre
					self.is_moving_down = True
					logger.debug("DESCEND vers position optimale")
					
			else:
				if self.is_moving_up:
					self.send_command(ws, 3)  # Arrêter de monter
					self.is_moving_up = False
				elif self.is_moving_down:
					self.send_command(ws, 4)  # Arrêter de descendre
					self.is_moving_down = False
				#logger.debug("STABLE à la position optimale")

			# Log des informations de debug
			# Mise à jour de la position précédente de la balle
			self.previous_ball_pos = self.ball_pos.copy()

		except Exception as e:
			logger.error(f"Erreur lors du mouvement prédictif: {str(e)}")

	def on_message(self, ws, message):
		data = json.loads(message)
		if data['type'] == 'export_data':
			logger.debug(f":::{data}")
		elif data['type'] == 'waiting_room':
			logger.debug("En attente d'un adversaire...")
		elif data['type'] == 'export_data':
			game_id = data['game_id']
			logger.debug("Jeu créé! ID du jeu :", game_id)
		elif data['type'] == 'game_start':
			logger.debug("Le jeu a commencé!")
		elif data['type'] == 'gu':
			current_time = time.time()
			if current_time - self.last_message_time > self.message_cooldown:
				self.last_message_time = current_time
				self.ball_pos = data['bp']
				self.paddle_pos = data['pp']
				self.calculate_ball_velocity()
				self.predicted_y = self.predict_ball_intersection()
				self.optimal_paddle_position = self.get_optimal_paddle_position(self.predicted_y)
				logger.debug(f"PADDLE POS : {self.paddle_pos}")
				logger.debug(f"PREDICTED Y : {self.predicted_y}")
				logger.debug(f"data :{data}")
			self.ft_move(ws, self.optimal_paddle_position)
		elif data['type'] == 'scored':
			logger.debug(data['msg'])
			# Réinitialiser les données de prédiction après un point
			self.previous_ball_pos = None
			self.ball_velocity = {'x': 0, 'y': 0}
		elif data['type'] == 'game_end':
			logger.debug(f"Jeu terminé. Raison: {data['reason']}")
			ws.close()

	def send_command(self, ws, command):
		ws.send(json.dumps({
			'type': 'move',
			'input': command
		}))
		logger.debug(f"Commande envoyée: {command}")

	def on_error(self, ws, error):
		logger.debug(f"Erreur: {error}")

	def on_close(self, ws):
		logger.debug("Connexion WebSocket fermée.")

	def on_open(self, ws):
		logger.debug("Connexion WebSocket établie.")
