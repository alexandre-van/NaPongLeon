import uuid
import random
import asyncio
from .logger import setup_logger

logger = setup_logger()

# Types de nourriture (proprietes)
FOOD_TYPES = {
	'common': {'value': 1, 'probability': 0.75, 'color': '#FFFF00'},
	'rare': {'value': 3, 'probability': 0.22, 'color': '#00FF00'},
	'epic': {'value': 8, 'probability': 0.03, 'color': '#FF00FF'}
}

# Types de power-ups (modifications possibles)
POWER_UPS = {
	'speed_boost': {
		'duration': 10,
		'probability': 0.1,
		'color': '#FFFFFF',
		'text_color': '#32CD32',
		'effect': 'speed_multiplier',
		'value': 1.25
	},
	'slow_zone': {
		'duration': 10,
		'probability': 0.1,
		'color': '#FFFFFF',
		'text_color': '#FF6B6B',
		'effect': 'speed_multiplier',
		'value': 0.7
	},
	'shield': {
		'duration': 8,
		'probability': 0.05,
		'color': '#FFFFFF',
		'text_color': '#C0C0C0',
		'effect': 'invulnerable',
		'value': True
	},
	'point_multiplier': {
		'duration': 10,
		'probability': 0.08,
		'color': '#FFFFFF',
		'text_color': '#FFA500',
		'effect': 'score_multiplier',
		'value': 2
	}
}

# Classe qui represente une game
class Game:
	# Constructeur de la classe
	def __init__(self, game_id, admin_id, expected_players):
		self.game_id = game_id
		self.admin_id = admin_id
		self.admin_consumer = None
		self.expected_players = expected_players
		self.players = {}
		self.food = []
		self.map_width = 10000
		self.map_height = 10000
		self.max_food = 2000
		self.player_inputs = {}
		self.player_movements = {}
		self.PLAYER_SPEED = 550
		self.status = "waiting"
		self.game_loop_task = None
		self.initialize_food()
		self.power_ups = []
		self.power_up_spawn_timer = 0
		self.power_up_spawn_interval = 5  # secondes

	""" FUNCTIONS FOOD """
	def initialize_food(self):
		"""Initialise la nourriture sur la carte"""
		for _ in range(self.max_food):
			self.add_food()

	def get_random_food_type(self):
		"""Randomisation du type de nourriture"""
		rand = random.random()
		cumulative_proba = 0
		for food_type, proba in FOOD_TYPES.items():
			cumulative_proba += proba['probability']
			if rand <= cumulative_proba:
				return food_type
		return 'common'

	def add_food(self, food_id=None):
		"""Ajoute de la nourriture sur la carte"""
		if len(self.food) >= self.max_food:
			return None
		
		food_type = self.get_random_food_type()
		new_food = {
			'id': str(uuid.uuid4()) if not food_id else food_id, # Si l'id n'est pas fourni, on le genere
			'x': random.randint(0, self.map_width), 			# Position x de la nourriture
			'y': random.randint(0, self.map_height), 			# Position y de la nourriture
			'type': food_type, 									# Type de nourriture
			'value': FOOD_TYPES[food_type]['value'], 			# Valeur de la nourriture
			'color': FOOD_TYPES[food_type]['color'] 			# Couleur de la nourriture
		}
		self.food.append(new_food)
		return new_food

	def distance(self, obj1, obj2):
		"""Calcule la distance entre deux objets avec la formule : d = √((x₂-x₁)² + (y₂-y₁)²)"""
		return ((obj1['x'] - obj2['x']) ** 2 + (obj1['y'] - obj2['y']) ** 2) ** 0.5

	def check_all_food_collisions(self):
		"""Envoie la fonction check_food_collision pour tous les joueurs"""
		food_changes = []
		for player_id in self.players:
			changes = self.check_food_collision(player_id)
			if changes:
				food_changes.extend(changes)
		return len(food_changes) > 0

	def check_food_collision(self, player_id):
		"""Vérifie les collisions entre un joueur et la nourriture"""
		player = self.players.get(player_id)
		if not player:
			return False
		
		changed_foods = []
		collision_occurred = False
		
		for food in self.food[:]:
			if self.distance(player, food) < player['size'] * 0.9:
				player['size'] += food['value'] * player['score_multiplier']
				player['score'] += food['value'] * player['score_multiplier']
				self.food.remove(food)
				new_food = self.add_food()
				if new_food:
					changed_foods.append(new_food)
				collision_occurred = True

		return changed_foods if collision_occurred else None # Si une collision a eu lieu, on retourne les nouvelles nourritures, sinon on retourne None

	"""		"""

	""" FUNCTIONS PLAYERS """
	def add_player(self, player_id, player_name):
		"""Ajoute un joueur à la partie"""
		if player_id not in self.expected_players:
			return False
		# logger.debug(f"ADDING A PLAYER :{player_id} : {player_name}")
		self.players[player_id] = {
			'id': player_id, # Id du joueur
			'name': player_name, # Nom du joueur
			'x': random.randint(0, self.map_width), # Position x du joueur
			'y': random.randint(0, self.map_height), # Position y du joueur
			'size': 30, # Taille du joueur
			'score': 0, # Score du joueur
			'color': f'#{random.randint(0, 0xFFFFFF):06x}', # Couleur du joueur
			'speed_multiplier': 1, # Multiplicateur de vitesse du joueur
			'invulnerable': False, # Invulnerabilité du joueur
			'score_multiplier': 1, # Multiplicateur de score du joueur
			'inventory': [None, None, None] # Inventaire du joueur
		}
		# Check si avec cet ajout la len de players est égale à la len de expected_players
		if len(self.players) == len(self.expected_players):
			self.status = 'in_progress' # Si oui, on passe le status de leur game à in_progress
		return True

	def remove_player(self, player_id):
		"""Retire un joueur de la partie"""
		# Le player (player_id) est forcemment le loser
		if player_id in self.players:
			loser = self.players[player_id] # On recupere le loser
			loser_score = self.players[player_id]['score']
			del self.players[player_id] # Et on le supprime de la liste des players
			if player_id in self.player_inputs:
				del self.player_inputs[player_id] # Et on le supprime de la liste des inputs de players
			if player_id in self.player_movements:
				del self.player_movements[player_id] # Pareil pour les movements
			if len(self.players) <= 1:
				self.status = "finished" # Quand la len de players est 1, on passe le status de leur game à finished (forcemment le cas)
				winner = list(self.players.values())[0]
				return {
					'type': 'game_finish',
					'status': self.status,
					'loser': loser,
					'loser_score': loser_score,
					'winner': winner,
					'winner_score': winner['score'],
					'message_winner': f"Final score : {winner['score']:.0f} ! GG !",
					'message_loser': f"Final score : {loser_score:.0f} ! NT !",
				}
		return None

	def player_eat_other_player(self, player_id, other_player_id):
		"""Quand un joueur mange un autre joueur"""
		player = self.players.get(player_id)
		other_player = self.players.get(other_player_id)
		if not player or not other_player:
			return False

		if self.distance(player, other_player) < (player['size'] + other_player['size']) / 2:
			if player['size'] > other_player['size'] * 1.2:
				# Mettre à jour le joueur qui mange ( si jamais le jeu pouvait continuer )
				player['size'] += other_player['size'] * 0.25
				player['score'] += other_player['score'] * 0.25
				
				# Supprimer le joueur mangé et retourner le résultat (dictionnaire)
				eaten = self.remove_player(other_player_id)
				if eaten:
					return eaten
		return False

	def handle_player_input(self, player_id, key, is_key_down):
		"""Gère les entrées des joueurs dans la game pour le consumer"""
		if player_id not in self.player_inputs:
			self.player_inputs[player_id] = {
				'w': False, 'a': False, 's': False, 'd': False,
				'arrowup': False, 'arrowleft': False, 'arrowdown': False, 'arrowright': False
			}
		self.player_inputs[player_id][key.lower()] = is_key_down

	"""		"""

	""" FUNCTIONS GAME LOOP """
	async def start_game_loop(self, broadcast_callback):
		"""Démarre la boucle de jeu"""
		# On cree la tache de la boucle de jeu
		self.game_loop_task = asyncio.create_task(self._game_loop(broadcast_callback))
		
	async def _game_loop(self, broadcast_callback):
		logger.debug("game loop starting...")
		"""Boucle de jeu principale"""
		try:
			last_update = asyncio.get_event_loop().time()
			await broadcast_callback(self.game_id, self.update_state(food_changes=True))
			while self.status != "finished" and self.status != 'aborted':
				while self.status == 'waiting':
					await asyncio.sleep(1/60)
				current_time = asyncio.get_event_loop().time()
				delta_time = current_time - last_update
				last_update = current_time
				positions_updated = self.update_positions(delta_time)
				if positions_updated:
					await broadcast_callback(self.game_id, self.update_state(food_changes=False)) # Send only updated positions to all players
				
				# Vérifier les collisions entre les deux joueurs
				if len(self.players) == 2:
					player_ids = list(self.players.keys())
					state_details = self.player_eat_other_player(player_ids[0], player_ids[1])
					if state_details:
						await broadcast_callback(self.game_id, state_details)
					state_details = self.player_eat_other_player(player_ids[1], player_ids[0])
					if state_details:
						await broadcast_callback(self.game_id, state_details)

				player_food_changes = self.check_all_food_collisions()
				if player_food_changes:
					await broadcast_callback(self.game_id, self.update_state(food_changes=True)) # Send food changes to all players

				# Vérifier les collisions avec les power-ups
				for player_id in self.players:
					collected_power_up = self.check_power_up_collision(player_id)
					if collected_power_up:
						await broadcast_callback(self.game_id, {
							'type': 'power_up_collected',
							'game_id': self.game_id,
							'players': self.players,
							'power_up': collected_power_up['power_up'],
							'power_ups': self.power_ups,
							'player_id': player_id
						})
				# Gestion des power-ups
				self.power_up_spawn_timer += delta_time
				if self.power_up_spawn_timer >= self.power_up_spawn_interval:
					self.power_up_spawn_timer = 0
					new_power_up = self.spawn_power_up()
					if new_power_up:
						await broadcast_callback(self.game_id, {
							'type': 'power_up_spawned',
							'game_id': self.game_id,
							'players': self.players,
							'power_up': new_power_up,
							'power_ups': self.power_ups
						})
				await asyncio.sleep(1/60)
			self.status = 'finished'
			await broadcast_callback(self.game_id, self.update_state(food_changes=False))
		except Exception as e:
			logger.error(f"Error in game loop for game {self.game_id}: {e}")

	"""		"""

	""" FUNCTIONS STATES """
	def update_state(self, food_changes=None):
		"""Retourne l'état mis à jour soit des joueurs soit de la nourriture"""
		game_state = self.get_food_state() if food_changes == True else self.get_players_state()
		return game_state

	def get_food_state(self):
		"""Retourne l'état complet de la partie"""
		return {
			'type': 'food_update',
			'game_id': self.game_id,
			'players': self.players,
			'food': self.food,
		}

	def get_players_state(self):
		"""Retourne l'état des joueurs"""
		return {
			'type': 'players_update',
			'game_id': self.game_id,
			'players': self.players,
		}

	"""		"""

	""" FUNCTIONS MOVEMENTS """

	def update_positions(self, delta_time):
		"""Met à jour les positions des joueurs"""
		positions_updated = False
		for player_id, inputs in self.player_inputs.items():
			if player_id not in self.players:
				continue

			dx = dy = 0
			if inputs['w'] or inputs['arrowup']: dy += 1
			if inputs['s'] or inputs['arrowdown']: dy -= 1
			if inputs['a'] or inputs['arrowleft']: dx -= 1
			if inputs['d'] or inputs['arrowright']: dx += 1

			if dx != 0 or dy != 0:
				player = self.players[player_id]
				base_speed = self.PLAYER_SPEED * player['speed_multiplier']
				if player['score'] <= 200:
					speed_factor = max(0.9, 1 - (player['score'] / 2300))
					speed = base_speed * speed_factor
				elif player['score'] <= 400:
					speed_factor = max(0.8, 1 - (player['score'] / 2300))
					speed = base_speed * speed_factor
				elif player['score'] <= 800:
					speed_factor = max(0.6, 1 - (player['score'] / 2300))
					speed = base_speed * speed_factor
				elif player['score'] <= 1000:
					speed = base_speed * 0.6
				else:
					speed = base_speed * 0.5
				
				new_x = player['x'] + dx * speed * delta_time
				new_y = player['y'] + dy * speed * delta_time
				
				new_x = max(0, min(new_x, self.map_width))
				new_y = max(0, min(new_y, self.map_height))
				
				if abs(new_x - player['x']) > 0.01 or abs(new_y - player['y']) > 0.01:
					player['x'] = new_x
					player['y'] = new_y
					positions_updated = True
				player['current_speed'] = round(speed)
		return positions_updated

	"""		"""

	""" FUNCTIONS POWER-UPS """
	def spawn_power_up(self):
		if len(self.power_ups) >= 9:
			return None
			
		power_up_type = random.choice(list(POWER_UPS.keys()))
		power_up = {
			'id': str(uuid.uuid4()),
			'type': power_up_type,
			'x': random.randint(0, self.map_width),
			'y': random.randint(0, self.map_height),
			'properties': POWER_UPS[power_up_type]
		}
		self.power_ups.append(power_up)
		return power_up

	def check_power_up_collision(self, player_id):
		player = self.players.get(player_id)
		if not player:
			return False

		for power_up in self.power_ups[:]:
			if self.distance(player, power_up) < player['size']:
				# Trouver le premier slot vide
				empty_slot = next((i for i, slot in enumerate(player['inventory']) if slot is None), -1)
				if empty_slot != -1:  # Si un slot vide est trouvé
					collected_power_up = power_up
					player['inventory'][empty_slot] = power_up
					self.power_ups.remove(power_up)
					return {
						'type': 'power_up_collected',
						'power_up': collected_power_up,
						'player_id': player_id,
					}
		return False

	def use_power_up(self, player_id, slot_index):
		player = self.players.get(player_id)
		if not player:
			return False
		try:
			# Vérifier que l'index est valide et que le slot n'est pas vide
			if 0 <= slot_index < len(player['inventory']) and player['inventory'][slot_index] is not None:
				power_up = player['inventory'][slot_index]
				# Vider le slot spécifique
				player['inventory'][slot_index] = None
				
				# Appliquer l'effet du power-up
				self.apply_power_up(player_id, power_up)
				return {
					'type': 'power_up_used',
					'player_id': player_id,
					'power_up': power_up,
					'players': self.players,
				}
		except Exception as e:
			logger.error(f"Error using power-up: {e}")
		return False

	def apply_power_up(self, player_id, power_up):
		player = self.players[player_id]
		effect = power_up['properties']['effect']
		value = power_up['properties']['value']
		duration = power_up['properties']['duration']
		
		if effect == 'speed_multiplier':
			player['speed_multiplier'] = value
		elif effect == 'invulnerable':
			player['invulnerable'] = value
		elif effect == 'score_multiplier':
			player['score_multiplier'] = value

		# Planifier la fin de l'effet
		asyncio.create_task(self.remove_power_up_effect(player_id, effect, duration))

	async def remove_power_up_effect(self, player_id, effect, duration):
		await asyncio.sleep(duration)
		if player_id in self.players:
			player = self.players[player_id]
			if effect == 'speed_multiplier':
				player['speed_multiplier'] = 1
			elif effect == 'invulnerable':
				player['invulnerable'] = False
			elif effect == 'score_multiplier':
				player['score_multiplier'] = 1
	
	"""		"""

	""" FUNCTIONS CLEANUP """
	async def cleanup(self):
		"""Nettoie les donnees de la partie"""
		logger.info(f"Cleaning up game {self.game_id}")
		
		# Arrêter la boucle de jeu si elle est en cours
		if self.game_loop_task:
			self.game_loop_task.cancel()
			try:
				await self.game_loop_task
			except asyncio.CancelledError:
				logger.debug(f"Game loop for game {self.game_id} cancelled successfully")
			except Exception as e:
				logger.error(f"Error while cancelling game loop for game {self.game_id}: {e}")
		
		# Si jamais la game n'est pas finished, on la passe en aborted pour comprendre que la game a ete annulee
		if self.status != "finished":
			self.status = "aborted"
		
		self.players.clear()
		self.food.clear()
		self.power_ups.clear()
		self.player_inputs.clear()
		self.player_movements.clear()
		self.power_up_spawn_timer = 0
		logger.info(f"Game {self.game_id} cleaned up successfully")
	"""		"""
