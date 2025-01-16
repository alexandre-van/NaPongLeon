# matchmaking.py
from django.conf import settings
from game_manager.game_manager import Game_manager
from game_manager.utils.logger import logger
from game_manager.utils.timer import Timer
import uuid
import asyncio
import threading
import copy

class Matchmaking:
	matchmaking_instance = None
	
	def __init__(self):
		logger.debug("Matchmaking init...")
		self._is_running = False
		self._task = None
		self._is_running_mutex = threading.Lock()
		self._queue = {}
		self._queue_mutex = threading.Lock()
		self.GAME_MODES = copy.deepcopy(settings.GAME_MODES)

	async def remove_player_request(self, username):
		with self._queue_mutex:
			await Game_manager.game_manager_instance.update_player_status(username, 'inactive')
			await self._remove_player_request_in_queue(username)

	async def add_player_request(self, username, game_mode, modifiers, number_of_players, consumer):
		status = await Game_manager.game_manager_instance.get_player_status(username)
		if status == 'in_queue':
			await self.remove_player_request(username)
		elif status != 'inactive':
			logger.debug(f"Player {username} cannot join queue, status is '{status}'")
			await consumer.send_json({
				'status': 'error',
				'message': f"Cannot join queue with status '{status}'"
			})
			return

		await Game_manager.game_manager_instance.update_player_status(username, 'in_queue')
		queue_name = self.generate_queue_name(game_mode, modifiers, number_of_players)
		
		with self._queue_mutex:
			if queue_name not in self._queue:
				self._queue[queue_name] = []
			self._queue[queue_name].append({
				'username': username,
				'game_mode': game_mode,
				'modifiers': modifiers,
				'number_of_players': number_of_players,
				'consumer': consumer,
				'win_rate': await Game_manager.get_or_create_win_rate(username, game_mode),
				'tolerance': 0.05,
				'time': Timer(),
			})
		
		await consumer.send_json({
			'status': 'queued',
			'message': 'Joined matchmaking queue'
		})

	def generate_queue_name(self, game_mode, modifiers_list, number_of_players):
		queue_name = ""
		queue_name += number_of_players
		for i, gm in enumerate(self.GAME_MODES):
			if gm == game_mode:
				queue_name = chr(i + ord('0'))
				if self.GAME_MODES[game_mode]['modifier_list']:
					valid_modifiers = self.GAME_MODES[game_mode]['modifier_list']
					for y, m in enumerate(valid_modifiers):
						if m in modifiers_list:
							queue_name += chr(y + ord('0'))
					break
		return queue_name


	async def matchmaking_logic(self):
		with self._queue_mutex:
			for queue in list(self._queue.keys()):
				logger.info(f"# Traitement de la file d'attente : {queue}")

				if queue not in self._queue:
					logger.info(f"# La file d'attente {queue} n'existe plus. Continuation...")
					continue

				# Supprimer les clients déconnectés
				await self.remove_disconnected_client(self._queue[queue], False)
				logger.info(f"# Clients déconnectés retirés pour la file {queue}.")

				# Contiendra les différentes queues sélectionnées
				selected_queues = []

				# Parcourir la file principale
				for player_request in self._queue[queue][:]:
					logger.info(f"# Traitement de la requête du joueur : {player_request['username']}, win_rate : {player_request['win_rate']}, tolerance : {player_request.get('tolerance', 0.1)}")

					# Trouver ou créer une file sélectionnée adaptée
					added_to_queue = False
					for selected_queue in selected_queues:
						logger.info(f"# Vérification d'une file sélectionnée : {selected_queue['game_mode']} avec {len(selected_queue['queue'])}/{selected_queue['required_players']} joueurs.")

						# Vérifier si le joueur peut être ajouté à cette file sélectionnée
						if (
							abs(player_request['win_rate'] - selected_queue['average_win_rate']) <= 
							(player_request['tolerance'] + selected_queue['average_tolerance'])
							and len(selected_queue['queue']) < selected_queue['required_players']
						):
							logger.info(f"# Le joueur {player_request['username']} correspond à cette file sélectionnée.")
							selected_queue['queue'].append(player_request)
							# Réactualiser les métriques de la file sélectionnée
							selected_queue['average_win_rate'] = (
								sum(p['win_rate'] for p in selected_queue['queue']) / len(selected_queue['queue'])
							)
							selected_queue['average_tolerance'] = (
								sum(p['tolerance'] for p in selected_queue['queue']) / len(selected_queue['queue'])
							)
							added_to_queue = True
							break

					# Si aucune file sélectionnée ne convient, en créer une nouvelle
					if not added_to_queue:
						game_mode = player_request.get('game_mode')
						modifiers = player_request.get('modifiers')
						number_of_players = self.GAME_MODES.get(game_mode).get('number_of_players')
						if not number_of_players:
							team_size = int(self.GAME_MODES.get(game_mode).get('team_size'))
							number_of_players = int(player_request.get('number_of_players')) * team_size

						logger.info(f"# Création d'une nouvelle file sélectionnée pour le mode {game_mode}.")
						selected_queues.append({
							'queue': [player_request],
							'average_win_rate': player_request['win_rate'],
							'average_tolerance': player_request['tolerance'],
							'required_players': number_of_players,
							'game_mode': game_mode,
							'modifiers': modifiers,
						})

				# Parcourir les files sélectionnées pour compléter les matchs
				for selected_queue in selected_queues[:]:
					logger.info(f"# Vérification de la file sélectionnée : {selected_queue['game_mode']} avec {len(selected_queue['queue'])}/{selected_queue['required_players']} joueurs.")

					if len(selected_queue['queue']) == selected_queue['required_players']:
						logger.info(f"# Match trouvé pour le mode {selected_queue['game_mode']} avec {len(selected_queue['queue'])} joueurs.")
						await self.notify(
							selected_queue['game_mode'],
							selected_queue['modifiers'],
							selected_queue['queue']
						)
						selected_queues.remove(selected_queue)
					else:
						# Augmenter la tolérance pour les requêtes dans cette file sélectionnée
						for player_request in selected_queue['queue']:
							player_request['tolerance'] = min(player_request['tolerance'] + 0.005, 1)  # Limiter à 1 maximum
							logger.info(f"# Augmentation de la tolérance du joueur {player_request['username']} à {player_request['tolerance']:.2f}.")

						# Réactualiser la tolérance moyenne
						selected_queue['average_tolerance'] = (
							sum(p['tolerance'] for p in selected_queue['queue']) / len(selected_queue['queue'])
						)
						logger.info(f"# Nouvelle tolérance moyenne pour la file {selected_queue['game_mode']} : {selected_queue['average_tolerance']:.2f}.")





	async def notify(self, game_mode, modifiers, queue_selected):
		logger.debug(f'New group for game_mode {game_mode}!')
		game_id = str(uuid.uuid4())
		admin_id = str(uuid.uuid4())
		players = [p['username'] for p in queue_selected]
		game = None
		game_connected = False
		players_connected = False

		try:
			game_connected = await Game_manager.game_manager_instance.connect_to_game(
				game_id, admin_id, game_mode, modifiers, players)
			if game_connected:
				game = await Game_manager.game_manager_instance.create_new_game_instance(
					game_id, game_mode, modifiers, players)
				if game:
					for player_request in queue_selected:
						try:
							await player_request['consumer'].send_json({
								'status': 'game_found',
								'game_id': game_id,
								'service_name': self.GAME_MODES[game_mode]['service_name']
							})
							players_connected = True
						except Exception as e:
							logger.error(f"Error notifying player {player_request['username']}: {str(e)}")
							players_connected = False
							break
		except Exception as e:
			logger.error(f"Error in notify: {str(e)}")
			players_connected = False
		await self.remove_disconnected_client(queue_selected, players_connected)
		if not players_connected:
			if game_connected:
				await Game_manager.game_manager_instance.disconnect_to_game(game_id, game_mode)
				logger.debug(f'Game service {game_id} aborted')
			if game:
				await Game_manager.game_manager_instance.abord_game_instance(game)
				logger.debug(f'Game {game_id} aborted')

	async def remove_disconnected_client(self, queue, players_connected):
		for player_request in queue:
			username = player_request['username']
			if not players_connected:
				consumer = player_request['consumer']
				if not consumer.closed:
					continue
				await Game_manager.game_manager_instance.update_player_status(username, 'inactive')
			await self._remove_player_request_in_queue(username)
			logger.debug(f"{username} is removed")

	# LOOP

	async def matchmaking_loop(self):
		logger.debug("matchmaking loop started")
		while True:
			with self._is_running_mutex:
				if not self._is_running:
					break
			await self.matchmaking_logic()
			await asyncio.sleep(0.5)

	async def start_matchmaking_loop(self):
		with self._is_running_mutex:
			self._is_running = True
		self._task = asyncio.create_task(self.matchmaking_loop())
		try:
			await self._task
		except asyncio.CancelledError:
			logger.debug("Matchmaking loop has been cancelled.")
		finally:
			logger.debug("Exiting matchmaking loop.")

	def stop_matchmaking(self):
		logger.debug("Matchmaking stopping...")
		with self._is_running_mutex:
			self._is_running = False
			if self._task:
				self._task.cancel()

	# unproteged

	async def _get_player_request(self, username):
		for queue in list(self._queue.keys()):
			for player_request in self._queue[queue][:]:
				if player_request['username'] == username:
					return player_request
		return None

	async def _remove_player_request_in_queue(self, username):
		player_request = await self._get_player_request(username)
		if player_request is None:
			return None
		queuename = self.generate_queue_name(player_request['game_mode'], player_request['modifiers'], player_request['number_of_players'])
		queue = self._queue.get(queuename)
		if queue:
			queue.remove(player_request)

# Initialisation singleton
if Matchmaking.matchmaking_instance is None:
	Matchmaking.matchmaking_instance = Matchmaking()