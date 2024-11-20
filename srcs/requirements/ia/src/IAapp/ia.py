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
		self.previous_velocity = {'x': 0, 'y': 0}

		self.predicted_y = 0
		self.optimal_paddle_position = 0

		self.paddle_hit = False
		self.player = 'p2'

		self.last_message_time = 0
		self.message_cooldown = 0.1 # 1 seconde de délai

		# Constantes du terrain
		self.paddle_speed = 30
		self.COURT_HEIGHT = 32  # Hauteur du terrain (-30 à 30)
		self.COURT_WIDTH = 42   # Largeur du terrain (-42 à 42)
		self.PADDLE_HEIGHT = 12 # Hauteur de la raquette
		self.PADDLE_MAX_Y = 26  # Position Y maximale de la raquette
		self.PADDLE_MIN_Y = -26 # Position Y minimale de la raquette

		# Initialisation de votre IA
		logger.debug("IA instantiated.")


	def time_to_reach_target(self, current_y, target_y):
		"""
		Calcule le temps nécessaire pour que la raquette atteigne une position Y donnée.
		:param current_y: Position actuelle de la raquette en Y.
		:param target_y: Position cible en Y.
		:return: Temps en secondes.
		"""
		distance = abs(target_y - current_y)
		return distance / self.paddle_speed

 
	def calculate_ball_velocity(self):
		"""
		Calcule la vélocité de la balle en détectant les changements brusques de direction
		qui indiquent un rebond récent
		"""
		if self.previous_ball_pos is not None:
		# Calculer la nouvelle vélocité
			current_velocity = {
			'x': self.ball_pos['x'] - self.previous_ball_pos['x'],
			'y': self.ball_pos['y'] - self.previous_ball_pos['y']
		}
		else:
			self.ball_velocity = {'x': 0, 'y': 0}
			return
		
		if self.previous_velocity != {'x': 0, 'y': 0}:
			# Si la direction en y a changé brutalement, c'est qu'il y a eu un rebond
			if (self.previous_velocity['y'] * current_velocity['y'] < 0 and 
				abs(self.previous_velocity['y']) > 0.1):  # Pour éviter les faux positifs quand la vélocité est proche de 0
				#logger.debug("Rebond détecté!")
				# On garde la même amplitude de vélocité mais dans la direction opposée
				self.ball_velocity = {
					'x': current_velocity['x'],
					'y': -self.previous_velocity['y']  # On garde la vélocité précédente mais inversée
				}
			else:
				self.ball_velocity = current_velocity
		else:
			self.ball_velocity = current_velocity
			
		# Sauvegarder la vélocité pour la prochaine comparaison
		self.previous_velocity = self.ball_velocity
		
		#logger.debug(f"Vélocité calculée : {self.ball_velocity}")

	def predict_ball_intersection(self):
		"""
		Prédit le point d'intersection de la balle avec le plan de la raquette
		Retourne la position y prédite ou None si la balle s'éloigne
		"""
		if self.ball_velocity['x'] == 0:
			return 0
		if (self.player == 'p1'):
			# Si la balle s'éloigne de notre raquette
			if self.ball_velocity['x'] > 0:
				return 0
			# Position x de notre raquette
			paddle_x = -39
		else:
			if self.ball_velocity['x'] < 0:
				return 0
			paddle_x = 39

		# Calcul du temps jusqu'à l'intersection
		distance_to_paddle = paddle_x - self.ball_pos['x']
		time_to_intersection = distance_to_paddle / self.ball_velocity['x']

		# Calcul de la position y prédite
		self.predicted_y = self.ball_pos['y'] + (self.ball_velocity['y'] * time_to_intersection)

		# Prise en compte des rebonds
		bounces = 0
		while abs(self.predicted_y) > self.COURT_HEIGHT:  # Rebonds sur les murs (32 ou -32)
			if self.predicted_y > self.COURT_HEIGHT:
				self.predicted_y = 2 * self.COURT_HEIGHT - self.predicted_y  # Rebond sur le mur supérieur
			elif self.predicted_y < -self.COURT_HEIGHT:
				self.predicted_y = -2 * self.COURT_HEIGHT - self.predicted_y  # Rebond sur le mur inférieur
			bounces += 1
			if bounces > 10:  # Limite de sécurité pour éviter une boucle infinie
				break

		return self.predicted_y

	def get_optimal_paddle_position(self, predicted_y):
		"""
		Détermine la position optimale de la raquette en fonction de la prédiction
		"""
		if predicted_y is None:
			return self.paddle_pos[self.player]  # Maintenir la position actuelle

		# Limiter la position aux bornes permises pour la raquette
		self.optimal_paddle_position = max(self.PADDLE_MIN_Y, min(self.PADDLE_MAX_Y, predicted_y))

		return self.optimal_paddle_position

	def ft_move(self, ws, optimal_position, p):
		"""
		Déplace la raquette de manière prédictive en fonction de la trajectoire calculée
		"""
		try:
			# Marge de tolérance adaptée à l'échelle du terrain
			TOLERANCE = 1.5  # Augmentée car l'échelle est plus grande

			# Décision de mouvement basée sur la position optimale
			if self.paddle_pos[p] + TOLERANCE < optimal_position:
				if not self.is_moving_up:
					if self.is_moving_down:
						self.send_command(ws, 4)  # Arrêter de descendre
						self.is_moving_down = False
					self.send_command(ws, 1)  # Monter
					self.is_moving_up = True
					#logger.debug("MONTE vers position optimale")

			elif self.paddle_pos[p] - TOLERANCE > optimal_position:
				if not self.is_moving_down:
					if self.is_moving_up:
						self.send_command(ws, 3)  # Arrêter de monter
						self.is_moving_up = False
					self.send_command(ws, 2)  # Descendre
					self.is_moving_down = True
					#logger.debug("DESCEND vers position optimale")
					
			else:
				if self.is_moving_up:
					self.send_command(ws, 3)  # Arrêter de monter
					self.is_moving_up = False
				elif self.is_moving_down:
					self.send_command(ws, 4)  # Arrêter de descendre
					self.is_moving_down = False
				#logger.debug("STABLE à la position optimale")

			# Mise à jour de la position précédente de la balle
			self.previous_ball_pos = self.ball_pos.copy()

		except Exception as e:
			logger.error(f"Erreur lors du mouvement prédictif: {str(e)}")

	def ft_move_by_timer(self, timer, target, pos_actuel, ws):
		TOLERANCE = 1.5
		start_time = time.time()
		if (pos_actuel + TOLERANCE < target):
			if not self.is_moving_up:
				if self.is_moving_down:
					self.send_command(ws, 4)  # Arrêter de descendre
					self.is_moving_down = False
				self.send_command(ws, 1)  # Monter
				self.is_moving_up = True
			if (timer > time.time() - start_time):
			
		
		return
     
	def on_message(self, ws, message):
		data = json.loads(message)
		if data['type'] == 'waiting_room':
			logger.debug("En attente d'un adversaire...")
			self.player = 'p1'
		elif data['type'] == 'export_data':
			logger.debug(f":::{data}")
			data = data['data']
			# logger.debug(f"LEFT:::{data['left_player']}")
			# logger.debug(f"RIGHT:::{data['right_player']}")
			# logger.debug(f"US:::{self.player}")
			if data['left_player'] == self.player:
				self.player = 'p1'
			else:
				self.player = 'p2'
		elif data['type'] == 'export_data':
			game_id = data['game_id']
			logger.debug("Jeu créé! ID du jeu :", game_id)
		elif data['type'] == 'padel_contact':
			logger.debug("Contact avec la raquette!")
			self.paddle_hit = True
			self.ball_velocity = data['bs']
			self.predicted_y = self.predict_ball_intersection()
			self.optimal_paddle_position = self.get_optimal_paddle_position(self.predicted_y)
			time_start = time.time()
			self.ft_move_by_timer(time_start, self.optimal_paddle_position, self.paddle_pos[self.player], ws)
			#self.ft_move(ws, self.optimal_paddle_position, self.player)

		elif data['type'] == 'game_start':
			logger.debug("Le jeu a commencé!")
		elif data['type'] == 'gu':
			current_time = time.time()
			if current_time - self.last_message_time > self.message_cooldown:
				self.last_message_time = current_time
				self.ball_pos = data['bp']
				self.paddle_pos = data['pp']
				if (self.paddle_hit == False):
					self.calculate_ball_velocity()	
					self.predicted_y = self.predict_ball_intersection()
					self.optimal_paddle_position = self.get_optimal_paddle_position(self.predicted_y)
					self.ft_move(ws, self.optimal_paddle_position, self.player)
					
				logger.debug(f"optimal_paddle_position : {self.optimal_paddle_position}")
			#logger.debug(f"FT_MOVE : predicted y : {self.optimal_paddle_position} et {data}")
		elif data['type'] == 'scored':
			logger.debug(data['msg'])
			# Réinitialiser les données de prédiction après un point
			self.previous_ball_pos = None
			self.ball_velocity = {'x': 0, 'y': 0}
			self.previous_velocity = {'x': 0, 'y': 0}
			self.optimal_paddle_position = 0
			self.paddle_hit = False
		elif data['type'] == 'game_end':
			logger.debug(f"Jeu terminé. Raison: {data['reason']}")
			ws.close()

	def send_command(self, ws, command):
		ws.send(json.dumps({
			'type': 'move',
			'input': command
		}))
		#logger.debug(f"Commande envoyée: {command}")

	def on_error(self, ws, error):
		logger.debug(f"Erreur: {error}")

	def on_close(self, ws):
		logger.debug("Connexion WebSocket fermée.")

	def on_open(self, ws):
		logger.debug("Connexion WebSocket établie.")
