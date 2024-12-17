# ia.py
import json
import time
from .logger import logger

class IA:
	def __init__(self, ia_id):
		# info sur la balle
		self.ball_pos = {'x': 0, 'y': 0, 'z': 1}
		self.paddle_pos = {'p1': 0.0, 'p2': 0.0}
		self.is_moving_up = False
		self.is_moving_down = False

		self.ball_velocity = {'x': 0, 'y': 0}

		# prediction et position optimale du paddle
		self.predicted_y = 0
		self.optimal_paddle_position = 0

		# info sur joueur droit ou gauche
		self.paddle_hit = False
		self.player = 'AI'

		# delai de 1 seconde a respecter
		self.last_message_time = 0
		self.message_cooldown = 1 # 1 seconde de délai
		self.last_padel_contact = 0

		self.time_reach_target = time.time()
		self.time_start = time.time()

		# Constantes du terrain
		self.paddle_speed = 0
		self.COURT_HEIGHT = 2  # Hauteur du terrain (-32 à 32 de base)
		self.COURT_WIDTH = 3   # Largeur du terrain (-43 à 43)
		self.PADDLE_HEIGHT = 2 # Hauteur de la raquette
		self.PADDLE_MAX_Y = 6  # Position Y maximale de la raquette
		self.PADDLE_MIN_Y = 6 # Position Y minimale de la raquette
		self.paddle_x = 0

		# Initialisation de votre IA
		logger.debug("IA instantiated.")
  
	def parsing(self, data):
		"""
		Rentre toutes les constantes du terrain
		"""
		logger.debug(f"PADEL{data['padel']}")
		padel = data['padel']
  
		self.paddle_speed = padel['spd']
  
		padel_pos = padel['pos']
		if self.player != 'p2':
			self.paddle_x = -padel_pos['x']
		else:
			self.paddle_x = padel_pos['x']

		padel_size = padel['size']
		self.PADDLE_HEIGHT = padel_size['y']
		logger.debug(f"paddle height {self.PADDLE_HEIGHT}")
  
		arena = data['arena']
		arena = arena['size']
		self.COURT_WIDTH = arena['x'] / 2
		self.COURT_HEIGHT = arena ['y'] / 2
  
		self.PADDLE_MAX_Y = self.COURT_HEIGHT - self.PADDLE_HEIGHT / 2
		self.PADDLE_MIN_Y = -self.PADDLE_MAX_Y
  
		logger.debug(f"Base : PADDLE_MAX_Y :{self.PADDLE_MAX_Y} et PADDLE_MIN_Y{self.PADDLE_MIN_Y}\npos paddle x = {self.paddle_x}\n court height = {self.COURT_HEIGHT}")
  
	def time_to_reach_target(self, current_y, target_y):
		"""
		Calcule le temps nécessaire pour que la raquette atteigne une position Y donnée.
		:param current_y: Position actuelle de la raquette en Y.
		:param target_y: Position cible en Y.
		:return: Temps en secondes.
		"""
		distance = abs(target_y - current_y)
		return distance / self.paddle_speed

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
		else:
			if self.ball_velocity['x'] < 0:
				return 0

		# Calcul du temps jusqu'à l'intersection
		distance_to_paddle = self.paddle_x - self.ball_pos['x']
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

	def ft_move_by_timer(self, timer, timer_to_reach, target, pos_actuel, ws):
		""" Deplace le paddle a la position souhaite (target) tout en prenant en compte le temps pour savoir a quelle moment s'arreter de monter

		Args:
			timer : le moment ou la fonction est appele_
			timer_to_reach : le temps necessaire pour faire le deplacement
			target : la pos y cible du paddle
			pos_actuel : la derniere pos connu du paddle y avant l'actualisation
			ws : websocket
		"""	
		TOLERANCE = 0.5
		if (pos_actuel + TOLERANCE < target):
			if (timer_to_reach < time.time() - timer):
				if self.is_moving_up:
					self.send_command(ws, 3)  # Arrêter de monter
					self.is_moving_up = False
			elif not self.is_moving_up:
				if self.is_moving_down:
					self.send_command(ws, 4)  # Arrêter de descendre
					self.is_moving_down = False
				self.send_command(ws, 1)  # Monter
				self.is_moving_up = True

		elif (pos_actuel - TOLERANCE > target):
			if (timer_to_reach < time.time() - timer):
				if self.is_moving_down:
					self.send_command(ws, 4)
					self.is_moving_down = False
		
			elif not self.is_moving_down:
				if self.is_moving_up:
					self.send_command(ws, 3)
					self.is_moving_up = False
				self.send_command(ws, 2)
				self.is_moving_down = True
		else:
			if self.is_moving_up:
				self.send_command(ws, 3)
				self.is_moving_up = False
			elif self.is_moving_down:
				self.send_command(ws, 4)
				self.is_moving_down = False
		return
		
	def on_message(self, ws, message):
		data = json.loads(message)
		if data['type'] == 'waiting_room':
			logger.debug("En attente d'un adversaire...")
		elif data['type'] == 'export_data':
			logger.debug(f":::{data}")
			data = data['data']
			if self.player in data['teams']['left']:
				self.player = 'p1'
			else:
				self.player = 'p2'
			logger.debug(f"Joueur : {self.player}")
			self.parsing(data)
			ws.send(json.dumps({
			'type': 'ready',
			}))
		elif data['type'] == 'export_data':
			game_id = data['game_id']
			logger.debug("Jeu créé! ID du jeu :", game_id)
		elif data['type'] == 'padel_contact':
			current_time = time.time()
			# if data[QUETRU] != self.player:
			# else:
			# self.optimal_paddle_position = 0
			# self.time_start = time.time()
			# self.ft_move_by_timer(self.time_start, self.time_reach_target, self.optimal_paddle_position, self.paddle_pos[self.player], ws)
			if current_time - self.last_padel_contact > self.message_cooldown:
				self.last_padel_contact = current_time
				logger.debug(f"Contact avec la raquette! {data}")
				self.paddle_hit = True
				self.ball_pos = data['bp']
				self.paddle_pos = data['pp']
				self.ball_velocity = data['bs']
				self.predicted_y = self.predict_ball_intersection()
				self.optimal_paddle_position = self.get_optimal_paddle_position(self.predicted_y)
				self.time_reach_target = self.time_to_reach_target(self.paddle_pos[self.player], self.optimal_paddle_position)
				self.time_start = time.time()
				self.ft_move_by_timer(self.time_start, self.time_reach_target, self.optimal_paddle_position, self.paddle_pos[self.player], ws)
		elif data['type'] == 'game_start':
			logger.debug("Le jeu a commencé!")
		elif data['type'] == 'gu':
			current_time = time.time()
			if current_time - self.last_message_time > self.message_cooldown:
				self.last_message_time = current_time
				self.ball_pos = data['bp']
				self.paddle_pos = data['pp']
				if not self.paddle_hit:
					self.ball_velocity = data['bs']
					self.predicted_y = self.predict_ball_intersection()
					self.optimal_paddle_position = self.get_optimal_paddle_position(self.predicted_y)
					self.time_reach_target = self.time_to_reach_target(self.paddle_pos[self.player], self.optimal_paddle_position)
					self.time_start = time.time()
			self.ft_move_by_timer(self.time_start, self.time_reach_target, self.optimal_paddle_position, self.paddle_pos[self.player], ws)
		elif data['type'] == 'scored':
			logger.debug(data['msg'])
			# Réinitialiser les données de prédiction après un point
			self.ball_velocity = {'x': 0, 'y': 0}
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
		logger.debug(f"Commande envoyée: {command}")

	def on_error(self, ws, error):
		logger.debug(f"Erreur BELLLE: {error}")

	def on_close(self, ws, close_status_code, close_msg):
		logger.debug(
			f"Connexion WebSocket fermée. "
			f"Code : {close_status_code}, Message : {close_msg}"
		)

	def on_open(self, ws):
		logger.debug("Connexion WebSocket établie.")
