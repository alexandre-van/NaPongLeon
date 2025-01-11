import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .decorators import auth_required
from .Game import Game
from .logger import setup_logger

logger = setup_logger()

class GameConsumer(AsyncWebsocketConsumer):
	players = {}  # {player_id: websocket}
	active_games = {}  # {game_id: Game()}
	player_count = 0

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_id = None
		self.current_game_id = None
		self.last_status = None

	@auth_required
	async def connect(self, username=None, nickname=None):
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
		GameConsumer.player_count += 1
		self.player_name = nickname if nickname else username
		GameConsumer.players[self.player_id] = self

		# Envoyer la liste des parties disponibles
		await self.send_games_info()

	async def special_connection(self, game_id, special_id):
		game = GameConsumer.active_games.get(game_id)
		if game:
			if game.admin_id == special_id:
				await self.accept()
				game.admin_consumer = self
				await game.start_game_loop(self.broadcast_game_state)

	async def disconnect(self, close_code):
		logger.info(f"Player {self.player_id} disconnected with code {close_code}")

		if self.player_id in GameConsumer.players:
			GameConsumer.player_count -= 1
			del GameConsumer.players[self.player_id]
			logger.debug(f"Removed player {self.player_id} from players list")

		if self.current_game_id in GameConsumer.active_games:
			game = GameConsumer.active_games[self.current_game_id]
			# Informer les autres joueurs de la déconnexion immédiatement
			for player_id in game.players:
				if player_id != self.player_id and player_id in GameConsumer.players:
					await GameConsumer.players[player_id].send(text_data=json.dumps({
						'type': 'player_disconnected',
						'playerId': self.player_id
					}))
			dc = game.remove_player(self.player_id)
			if dc:
				await self.broadcast_game_state(self.current_game_id, dc)
			logger.debug(f"Removed player {self.player_id} from game {self.current_game_id}")

			# Si la partie est vide, on la nettoie et la supprime
			if len(game.players) == 0:
				logger.info(f"Game {self.current_game_id} is empty, cleaning up")
				await game.cleanup()
				del GameConsumer.active_games[self.current_game_id]
				for player_id in GameConsumer.players:
					games_info = []
					for game_id, game in GameConsumer.active_games.items():
						games_info.append({
							'gameId': game_id,
							'players': [{'name': p['name'], 'id': p['id']} for p in game.players.values()] ,
							'status': game.status
					})
					await GameConsumer.players[player_id].send(text_data=json.dumps({
						'type': 'player_disconnected',
						'games': games_info,
						'playerId': self.player_id
					}))
			else:
				# Informer les autres joueurs de la déconnexion
				logger.debug(f"Broadcasting updated game info after player disconnect")
				await self.broadcast_games_info_waitingroom()

	async def receive(self, text_data):
		data = json.loads(text_data)

		if data['type'] == 'start_game':
			self.current_game_id = data['game_id']
			# Recuperer la partie demander
			game = GameConsumer.active_games.get(self.current_game_id)
			if game:
				# Se connecter a la partie
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
		"""Envoie la liste des parties disponibles à tous les joueurs"""
		games_info = []
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
		"""Diffuse les informations sur les parties à tous les joueurs"""
		games_info = []
		for game_id, game in GameConsumer.active_games.items():
			games_info.append({
				'gameId': game_id,
				'players': [{'name': p['name'], 'id': p['id']} for p in game.players.values()] ,
				'status': game.status
			})

		for player in GameConsumer.players.values():
			await player.send(text_data=json.dumps({
				'type': 'update_waiting_room',
				'games': games_info,
				'players': game.players
			}))

	async def broadcast_game_state(self, game_id, state_update):
		logger.debug("broadcast_game_state")
		"""Diffuse les mises à jour du jeu aux joueurs"""
		if game_id not in GameConsumer.active_games:
			logger.error(f"Game {game_id} not found in active games.")
			return
		game = GameConsumer.active_games[game_id]
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
		message = {
			'type': state_update.get('type'),
			'game_id': state_update.get('game_id'),
			'players': state_update.get('players', {}),
		}

		# Ajout des mises à jour spécifiques
		if state_update['type'] == 'food_update':
			message.update({'food': state_update.get('food', [])})
		elif state_update['type'] in ['power_up_spawned', 'power_up_collected']:
			message.update({
				'power_up': state_update.get('power_up'),
				'power_ups': state_update.get('power_ups', [])
			})
		elif state_update['type'] == 'power_up_used':
			message.update({
				'slot_index': state_update.get('slot_index', -1),
				'power_up': state_update.get('power_up')
			})
		elif state_update['type'] == 'game_finish':
			loser = state_update.get('loser')
			if not loser:
				logger.error("Missing 'loser' in state update.")
				return

			# Notifier le gagnant
			winner = state_update.get('winner')
			if winner in GameConsumer.players:
				await GameConsumer.players[winner].send(text_data=json.dumps({
					'type': 'game_finish',
					'game_id': game_id,
					'players': game.players,
					'winner': winner,
					'loser': loser,
					'message_winner': state_update.get('message_winner'),
					'message_loser': state_update.get('message_loser')
				}))
			# Gérer le joueur mangé
			if loser in GameConsumer.players:
				# Retourner le joueur dans la salle d'attente
				await GameConsumer.players[loser].send(text_data=json.dumps({
					'type': 'game_finish',
					'game_id': game_id,
					'players': game.players,
					'winner': winner,
					'loser': loser,
					'message_winner': state_update.get('message_winner'),
					'message_loser': state_update.get('message_loser')
				}))
				await GameConsumer.players[loser].send_games_info()
			else:
				logger.warning(f"Eaten player {loser} not found in active players.")
			return

		# Envoie la mise à jour à tous les joueurs
		for player_id in game.players:
			if player_id in GameConsumer.players:
				await GameConsumer.players[player_id].send(text_data=json.dumps(message))
			else:
				logger.warning(f"Player {player_id} not found in GameConsumer.players.")


	@classmethod
	def create_new_game(cls, game_id, admin_id, expected_players):
		if game_id in cls.active_games:
			raise ValueError(f"A game with ID {game_id} already exists.")

		# Créer une nouvelle partie
		new_game = Game(game_id, admin_id, expected_players)
		cls.active_games[game_id] = new_game

		# Log de création de la partie
		logger.info(f"New game created with ID: {game_id}")
		return game_id
	
	@classmethod
	def abortgame(cls, game_id):
		if game_id in cls.active_games:
			game = cls.active_games.get(game_id)
			if game:
				game.cleanup()
			del cls.active_games[game_id]

	async def notify_admin_player_connection(self, game_id, username, connection_type='player'):
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