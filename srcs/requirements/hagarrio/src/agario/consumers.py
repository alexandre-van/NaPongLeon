import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .decorators import auth_required
from .Game import Game
from .logger import setup_logger

logger = setup_logger()

class GameConsumer(AsyncWebsocketConsumer):
	players = {}  # {player_id: dictionnaire du player}
	active_games = {}  # {game_id: Game()*} *instance de la classe Game

	# Constructeur de la classe
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_id = None
		self.current_game_id = None
		self.last_status = None

	# Decorateur qui verifie si l'utilisateur est authentifie
	@auth_required
	async def connect(self, username=None, nickname=None):
		"""Fonction qui se lance lorsqu'un utilisateur se connecte a l'iframe"""
		path = self.scope['path']
		segments = path.split('/')
		game_id = None
		special_id = None
		if len(segments) >= 4:
			game_id = segments[3]
		if len(segments) >= 6:
			special_id = segments[4]
		if game_id and special_id:
			await self.special_connection(game_id, special_id)
			return
		if username is None:
			logger.warning(f'An unauthorized connection has been received')
			return
		await self.accept()
		self.player_id = username
		self.player_name = nickname if nickname else username
		GameConsumer.players[self.player_id] = self
		# Envoyer la liste des parties disponibles
		await self.send_games_info()

	async def special_connection(self, game_id, special_id):
		"""Fonction qui se lance pour que l'admin se connecte a une game"""
		game = GameConsumer.active_games.get(game_id)
		if game:
			if game.admin_id == special_id:
				await self.accept()
				game.admin_consumer = self
				await game.start_game_loop(self.broadcast_game_state)

	async def disconnect(self, close_code):
		"""Fonction qui se lance lorsqu'un joueur se deconnecte"""
		logger.info(f"Player {self.player_id} disconnected with code {close_code}")
		# Supprimer le joueur de la liste 'players'
		if self.player_id in GameConsumer.players:
			del GameConsumer.players[self.player_id]
			logger.debug(f"Removed player {self.player_id} from players list")

		#Check si la game existe
		if self.current_game_id in GameConsumer.active_games:
			game = GameConsumer.active_games[self.current_game_id]
			# Informer les autres joueurs de la déconnexion (pour que le frontend mette a jour la liste des joueurs)
			for player_id in game.players:
				if player_id != self.player_id and player_id in GameConsumer.players:
					await GameConsumer.players[player_id].send(text_data=json.dumps({
						'type': 'player_disconnected',
						'playerId': self.player_id
					}))
			# Supprimer le joueur dans la game (fonction qui renvoie un message de type 'game_finish')
			dc = game.remove_player(self.player_id)
			if dc:
				#Vu qu'on recoit le message de type 'game_finish', on l'envoie a la fonction broadcast_game_state
				await self.broadcast_game_state(self.current_game_id, dc)
				logger.debug(f"Removed player {self.player_id} from game {self.current_game_id}")
				#Puis on envoie la liste des parties disponibles a tous les joueurs
				await self.broadcast_games_info_waitingroom()
				logger.debug(f"Broadcasting updated game info after player disconnect")
				#Enfin on supprime la game ("finished") de la liste des games actives
				del GameConsumer.active_games[self.current_game_id]


	async def receive(self, text_data):
		"""Fonction qui se lance lorsqu'un joueur envoie un message au serveur"""
		data = json.loads(text_data)

		if data['type'] == 'start_game':
			# Si le joueur était déjà dans une partie, nettoyons-la d'abord
			if self.current_game_id and self.current_game_id in GameConsumer.active_games:
				old_game = GameConsumer.active_games[self.current_game_id]
				if old_game.status == "finished":
					await old_game.cleanup()
					if len(old_game.players) == 0:
						del GameConsumer.active_games[self.current_game_id]
			
			self.current_game_id = data['game_id']
			# Recuperer la game demandee
			game = GameConsumer.active_games.get(self.current_game_id)
			if game:
				# Se connecter a la game
				authorized = game.add_player(self.player_id, self.player_name)
				if authorized:
					await self.notify_admin_player_connection(self.current_game_id, self.player_id)
					await self.broadcast_games_info_waitingroom()
					await self.send(text_data=json.dumps({
						'type': 'game_started',
						'gameId': game.game_id,
						'mapWidth': game.map_width,
						'mapHeight': game.map_height,
						'maxFood': game.max_food,
						'players': game.players,
						'food': game.food,
						'yourPlayerId': self.player_id
					}))
				else:
					await self.send(text_data=json.dumps({
						'type': 'error',
						'message': 'Unauthorized'
					}))

		elif data['type'] == 'input':
			if self.current_game_id in GameConsumer.active_games:
				game = GameConsumer.active_games[self.current_game_id]
				game.handle_player_input(self.player_id, data['key'], data['isKeyDown'])

		elif data['type'] == 'use_power_up':
			if self.current_game_id in GameConsumer.active_games:
				game = GameConsumer.active_games[self.current_game_id]
				# Récupérer le résultat de use_power_up
				power_up_state = game.use_power_up(self.player_id, data['slot'])
				if power_up_state:  # Si un power-up a été utilisé avec succès
					# Broadcast l'état mis à jour à tous les joueurs
					await self.broadcast_game_state(self.current_game_id, power_up_state)

	async def send_games_info(self):
		"""Envoie la liste des games disponibles a tous les joueurs dans la waiting room"""
		games_info = []
		# Creation de la liste des games disponibles avec toutes les informations necessaires
		for game_id, game in GameConsumer.active_games.items():
			games_info.append({
				'gameId': game_id,
				'players': [{'name': p['name'], 'id': p['id']} for p in game.players.values()] ,
				'status': game.status
			})

		await self.send(text_data=json.dumps({
			'type': 'waiting_room',
			'games': games_info,
			'yourPlayerId': self.player_id,
			'yourPlayerName': self.player_name
		}))

	async def broadcast_games_info_waitingroom(self):
		"""Meme fonction que send_games_info mais pour update waiting room avec un message different pour le frontend"""
		games_info = []
		for game_id, game in GameConsumer.active_games.items():
			games_info.append({
				'gameId': game_id,
				'players': [{'name': p['name'], 'id': p['id']} for p in game.players.values()] ,
				'status': game.status
			})

		# On a besoin car cette update se fait pendant les games et ne redirige pas vers la waiting room
		for player in GameConsumer.players.values():
			await player.send(text_data=json.dumps({
				'type': 'update_waiting_room',
				'games': games_info,
				'players': game.players,
				'yourPlayerId': self.player_id
			}))

	async def broadcast_game_state(self, game_id, state_update):
		"""FONCTION PRINCIPALE : Envoie les MAJ du jeu aux players"""
		if game_id not in GameConsumer.active_games:
			logger.error(f"Game {game_id} not found in active games.")
			return
		game = GameConsumer.active_games[game_id]
		if state_update:
			await self.notify_admin_teams(game_id, self.generate_teams(game.players))
			self.last_status = ""
		if game.status != self.last_status:
			win_team = None
			score = None
			if game.status == 'finished':
				if len(game.players) == 1:
					player = next(iter(game.players.values()))
					if player:
						win_team = player['id']
						score = player['score']
			await self.notify_admin_game_status(game_id, game.status, win_team, score)
		self.last_status = game.status
		# Creation du message a envoyer a tous les players
		message = {
			'type': state_update.get('type'),
			'game_id': state_update.get('game_id'),
			'players': state_update.get('players', {}),
		}
		# Ajout des informations specifiques a chaque message
		if state_update.get('type') == 'players_update':
			message.update({'yourPlayerId': self.player_id})
		elif state_update['type'] == 'food_update':
			message.update({'food': state_update.get('food', []), 'yourPlayerId': self.player_id})
		elif state_update['type'] == 'power_up_spawned':
			message.update({
				'power_up': state_update.get('power_up'),
				'power_ups': state_update.get('power_ups', [])
			})
		elif state_update['type'] == 'power_up_collected':
			message.update({
				'power_up': state_update.get('power_up'),
				'power_ups': state_update.get('power_ups', []),
				'player_id': state_update.get('player_id')
			})
		elif state_update['type'] == 'power_up_used':
			message.update({
				'slot_index': state_update.get('slot_index', -1),
				'power_up': state_update.get('power_up'),
				'players': state_update.get('players'),
				'player_id': state_update.get('player_id')
			})
		elif state_update['type'] == 'game_finish':
			loser = state_update.get('loser')
			loser_score = state_update.get('loser_score')
			if not loser:
				logger.error("Missing 'loser' in state update.")
				return			
			# Récupérer les IDs des joueurs
			winner = state_update.get('winner')
			winner_id = winner.get('id')
			loser_id = loser.get('id')
			await self.notify_admin_score_update(game_id, loser_id, loser_score)

			# Notifier le gagnant
			if winner_id in GameConsumer.players:
				await GameConsumer.players[winner_id].send(text_data=json.dumps({
					'type': 'victory',
					'status': state_update.get('status'),
					'game_id': game_id,
					'players': state_update.get('players'),
					'winner': winner,
					'loser': loser,
					'message_winner': state_update.get('message_winner'),
					'message_loser': state_update.get('message_loser')
				}))
				logger.info(f"Notified player {winner_id} about victory")
				await GameConsumer.players[winner_id].broadcast_games_info_waitingroom()

			# Gérer le joueur mangé (loser)
			if loser_id in GameConsumer.players:
				await GameConsumer.players[loser_id].send(text_data=json.dumps({
					'type': 'game_over',
					'status': state_update.get('status'),
					'game_id': game_id,
					'players': state_update.get('players'),
					'winner': winner,
					'loser': loser,
					'message_winner': state_update.get('message_winner'),
					'message_loser': state_update.get('message_loser')
				}))
				logger.info(f"Notified player {loser_id} about game over")
				await GameConsumer.players[loser_id].broadcast_games_info_waitingroom()
			else:
				logger.warning(f"Eaten player {loser_id} not found in active players.")
			return

		# Boucle qui envoie le message a tous les players de la game en question
		for player_id in game.players:
			if player_id in GameConsumer.players:
				await GameConsumer.players[player_id].send(text_data=json.dumps(message))
			else:
				logger.warning(f"Player {player_id} not found in GameConsumer.players.")


	# Le décorateur permet d'appeler cette méthode sur la classe elle-même plutôt que sur une instance
	@classmethod
	def create_new_game(cls, game_id, admin_id, expected_players):
		"""Cree une nouvelle game"""
		if game_id in cls.active_games:
			raise ValueError(f"A game with ID {game_id} already exists.")

		# Creation de la game
		new_game = Game(game_id, admin_id, expected_players)
		cls.active_games[game_id] = new_game
		logger.info(f"New game created with ID: {game_id}")
		return game_id

	
	# Le décorateur permet d'appeler cette méthode sur la classe elle-même plutôt que sur une instance
	@classmethod
	def abortgame(cls, game_id):
		"""Abort une game en cas d'erreur (ne devrait pas arriver)"""
		if game_id in cls.active_games:
			game = cls.active_games.get(game_id)
			if game:
				game.cleanup()
			del cls.active_games[game_id]

	async def notify_admin_player_connection(self, game_id, username, connection_type='player'):
		"""Notifie l'admin de la game que un player se connecte"""
		game = GameConsumer.active_games.get(game_id)
		if not game:
			logger.warning(f"Game {game_id} not found.")
			return
	
		admin_consumer = getattr(game, 'admin_consumer', None)
		if admin_consumer:
			message_type = f'{connection_type}_connection'
			await admin_consumer.send(text_data=json.dumps({
				'type': message_type,
				'username': username,
			}))
			logger.info(f"Notified admin of game {game_id} about {message_type} of {username}.")
		else:
			logger.warning(f"Admin for game {game_id} is not connected.")

	async def notify_admin_player_disconnection(self, game_id, username, disconnection_type='player'):
		"""Notifie l'admin de la game quand un player se deconnecte"""
		game = GameConsumer.active_games.get(game_id)
		if not game:
			logger.warning(f"Game {game_id} not found.")
			return
	
		admin_consumer = getattr(game, 'admin_consumer', None)
		if admin_consumer:
			message_type = f'{disconnection_type}_disconnection'
			await admin_consumer.send(text_data=json.dumps({
				'type': message_type,
				'username': username,
			}))
			logger.info(f"Notified admin of game {game_id} about {message_type} of {username}.")
		else:
			logger.warning(f"Admin for game {game_id} is not connected.")

	async def notify_admin_game_status(self, game_id, status, win_team=None, score=None):
		"""Notifie l'admin de la game quand la game change de status"""
		game = GameConsumer.active_games.get(game_id)
		if not game:
			logger.warning(f"Game {game_id} not found.")
			return

		admin_consumer = getattr(game, 'admin_consumer', None)
		if admin_consumer:
			payload = {
				'type': 'export_status',
				'status': status,
			}

			if status == 'finished' or status == 'aborted':
				if win_team:
					payload['team'] = win_team
				if score is not None:
					payload['score'] = score

			await admin_consumer.send(text_data=json.dumps(payload))
			logger.info(f"Notified admin of game {game_id} about game status: {status}.")
		else:
			logger.warning(f"Admin for game {game_id} is not connected.")

	async def notify_admin_score_update(self, game_id, team, score):
		"""Notifie l'admin de la game quand le score change"""
		game = GameConsumer.active_games.get(game_id)
		if not game:
			logger.warning(f"Game {game_id} not found.")
			return

		admin_consumer = getattr(game, 'admin_consumer', None)
		if admin_consumer:
			await admin_consumer.send(text_data=json.dumps({
				'type': 'update_score',
				'team': team,
				'score': score
			}))
			logger.info(f"Notified admin of game {game_id} about score update for team {team}.")
		else:
			logger.warning(f"Admin for game {game_id} is not connected.")

	def generate_teams(self, players):
		"""Creation des equipes pour l'admin et la database"""
		teams = {}
		if not players or len(players) < 1:
			return teams
		for username in players:
			teams[username] = [ username ]
		return teams

	async def notify_admin_teams(self, game_id, teams):
		"""Notifie l'admin de la game pour exporter les equipes"""
		game = GameConsumer.active_games.get(game_id)
		if not game:
			logger.warning(f"Game {game_id} not found.")
			return
		admin_consumer = getattr(game, 'admin_consumer', None)
		if admin_consumer:
			await admin_consumer.send(text_data=json.dumps({
					'type': "export_teams",
					'teams': teams
				}))
			logger.info(f"Notified admin of game {game_id} about team composition {teams}.")
		else:
			logger.warning(f"Admin for game {game_id} is not connected.")
