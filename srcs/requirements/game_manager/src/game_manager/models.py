from django.db import models
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.utils import timezone
from .utils.logger import logger

class GameMode(models.Model):
	name = models.CharField(max_length=100, unique=True)

	@classmethod
	def get_or_create(cls, game_mode):
		try:
			instance, created = cls.objects.get_or_create(name=game_mode)
			if instance:
				return instance
		except IntegrityError as e:
			logger.error(f"Integrity error while creating GameMode '{game_mode}': {e}")
			return None
		except DatabaseError as e:
			logger.error(f"Database error while creating GameMode '{game_mode}': {e}")
			return None
		return None

class Player(models.Model):
	STATUS_CHOICES = [
		('inactive', 'Player is inactive or not engaged in any activity'),
		('in_queue', 'Player is in a matchmaking queue'),
		('pending', 'Player is expected to join a game'),
		('waiting_for_players', 'Player is waiting for other players to join the game'),
		('loading_game', 'Player is waiting for the game to load'),
		('in_game', 'Player is currently playing in a game'),
		('spectate', 'Player is currently spectating a game'),
	]

	username = models.CharField(max_length=100, unique=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')

	def __str__(self):
		return self.username

	@classmethod
	def get_or_create_player(cls, username):
		try:
			player, created = cls.objects.get_or_create(username=username)
			if created:
				logger.info(f'Player account "{username}" successfully created.')
			return player
		except IntegrityError as e:
			logger.error(f"Integrity error while creating player '{username}': {e}")
			return None
		except DatabaseError as e:
			logger.exception(f"Unexpected database error while creating player '{username}': {e}")
			return None

	@classmethod
	def get_player(cls, username):
		try:
			player = cls.objects.get(username=username)
			return player
		except ObjectDoesNotExist:
			return None
		except IntegrityError as e:
			logger.error(f"Integrity error while fetching player '{username}': {e}")
			return None
		except DatabaseError as e:
			logger.exception(f"Unexpected database error while fetching player '{username}': {e}")
			return None

	def update_status(self, new_status):
		if new_status in dict(self.STATUS_CHOICES):
			logger.info(f"{self.username}, new status : {new_status}")
			self.status = new_status
			self.save()
		else:
			raise ValueError(f"Invalid status: {new_status}")
	
	def add_game_to_history(self, game_id):
		game = GameInstance.get_game(game_id)
		if game:
			PlayerGameHistory.objects.get_or_create(player=self, game=game)

	def get_game_history(self):
		return PlayerGameHistory.objects.filter(player=self).values_list('game__game_id', flat=True)



class PlayerGameHistory(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	game = models.ForeignKey('GameInstance', on_delete=models.CASCADE)
	game_date = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ('player', 'game')

class Team(models.Model):
	name = models.CharField(max_length=42)

	class Meta:
		unique_together = ('name',)

	@classmethod
	def get_or_create_team(cls, name):
		try:
			team, created = cls.objects.get_or_create(name=name)
			return team
		except IntegrityError as e:
			logger.error(f"Integrity error while creating team '{name}': {e}")
			return None
		except DatabaseError as e:
			logger.error(f"Database error while creating team '{name}'': {e}")
			return None

class GameInstance(models.Model):
	STATUS_CHOICES = [
		('waiting', 'Waiting for players to join'),
		('loading', 'Players are loading game assets and configurations'),
		('in_progress', 'Game currently in progress'),
		('aborting', 'Game has been aborted'),
		('aborted', 'Game has been aborted'),
		('finished', 'Game has finished'),
	]

	game_id = models.CharField(max_length=100, unique=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
	winner = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
	game_date = models.DateTimeField(default=timezone.now)
	
	# Changer de CharField à ForeignKey pour stocker l'instance de GameMode
	game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE)

	def __str__(self):
		return f"Game {self.game_id} - Status: {self.status} - Mode: {self.game_mode.name}"

	def is_finished(self):
		return self.status in ['finished', 'aborted']

	def update_status(self, new_status):
		if new_status in dict(self.STATUS_CHOICES):
			self.status = new_status
			self.save()
		else:
			raise ValueError(f"Invalid status: {new_status}")

	def set_winner(self, team):
		# Récupère ou crée l'équipe gagnante
		if self.winner is None:
			self.winner = Team.get_or_create_team(team)
			self.save()
	
			# Récupère tous les joueurs des équipes
			teams = GamePlayer.objects.filter(game=self)
		
			# Séparer les joueurs en fonction de leur équipe
			winning_players = teams.filter(team=self.winner)
			losing_players = teams.exclude(team=self.winner)
		
			# Met à jour les win_rate des joueurs gagnants et perdants
			for player_game in winning_players:
				self.update_win_rate(player_game.player, True)  # Gagnant
			for player_game in losing_players:
				self.update_win_rate(player_game.player, False)  # Perdant

	def update_win_rate(self, player, win):
		game_mode = self.game_mode

		# Récupérer ou créer l'instance de WinRate pour le joueur et le mode de jeu
		win_rate_instance, created = WinRate.objects.get_or_create(player=player, game_mode=game_mode)

		# Mettre à jour le nombre de victoires ou de défaites
		if win_rate_instance:
			if win:
				win_rate_instance.wins += 1
			else:
				win_rate_instance.losses += 1
			win_rate_instance.save()

	def abort_game(self):
		self.status = 'aborted'
		self.save()

	def aborting_game(self):
		if self.status != 'aborted':
			self.status = 'aborting'
			self.save()

	def update_score(self, team, score):
		team_instance = Team.get_or_create_team(team)
		if team_instance:
			game_score, created = GameScore.objects.get_or_create(game=self, team=team_instance)
			game_score.score = score
			game_score.save()

	def add_player_to_team(self, player_username, team_name):
		player = Player.get_player(player_username)
		if player:
			# Ensure team exists or create it
			team = Team.get_or_create_team(team_name)
			if team:
				game_player, created = GamePlayer.objects.get_or_create(game=self, player=player, team=team)
				if not created:
					logger.debug(f"Player {player.username} is already part of the game {self.game_id}.")

	def clean(self):
		usernames = GamePlayer.objects.filter(game=self).values_list('player__username', flat=True)
		if len(usernames) != len(set(usernames)):
			raise ValidationError("Usernames must be unique.")

	def save(self, *args, **kwargs):
		self.clean()
		super(GameInstance, self).save(*args, **kwargs)

	@classmethod
	def create_game(cls, game_id, game_mode, modifiers, usernames):
		try:
			# Ensure the game mode exists or create it
			game_mode_instance = GameMode.get_or_create(game_mode)
			if not game_mode_instance:
				logger.error(f"Invalid game mode '{game_mode}', aborting game creation.")
				return None

			new_game = cls(
				game_id=game_id,
				status='waiting',
				winner=None,
				game_mode=game_mode_instance  # Assign the GameMode instance
			)
			new_game.save()

			# Add players to the game
			for username in usernames:
				player = Player.get_player(username)
				if player:
					PlayerGameHistory.objects.get_or_create(player=player, game=new_game)

			# Add modifiers to the game
			for modifier_name in modifiers:
				modifier, _ = Modifiers.objects.get_or_create(name=modifier_name)
				ModifiersHistory.objects.get_or_create(game=new_game, modifier=modifier)

			logger.info(f"Game '{game_id}' created successfully with mode '{game_mode}' and modifiers {modifiers}.")
			return new_game
		except IntegrityError as e:
			logger.error(f"Integrity error while creating game '{game_id}': {e}")
			return None
		except DatabaseError as e:
			logger.error(f"Database error while creating game '{game_id}': {e}")
			return None


	@classmethod
	def get_game(cls, game_id):
		try:
			return cls.objects.get(game_id=game_id)
		except cls.DoesNotExist:
			return None


class GamePlayer(models.Model):
	game = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('game', 'player')

class GameScore(models.Model):
	game = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	score = models.IntegerField(default=0)

	class Meta:
		unique_together = ('game', 'team')

class Modifiers(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name

	@classmethod
	def get_modifier(cls, name):
		try:
			return cls.objects.get(name=name)
		except cls.DoesNotExist:
			logger.warning(f"Modifier '{name}' not found.")
			return None


class ModifiersHistory(models.Model):
	game = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
	modifier = models.ForeignKey(Modifiers, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('game', 'modifier')

	def __str__(self):
		return f"Game: {self.game.game_id}, Modifier: {self.modifier.name}"

class WinRate(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE)
	wins = models.PositiveIntegerField(default=0)
	losses = models.PositiveIntegerField(default=0)
	
	@property
	def win_rate(self):
		total_games = self.wins + self.losses
		if total_games == 0:
			return 0.5
		return self.wins / total_games
	
	@classmethod
	def get_or_create_win_rate(cls, player, game_mode):
		try:
			instance, created = cls.objects.get_or_create(player=player, game_mode=game_mode)
			if instance:
				return instance.win_rate
		except IntegrityError as e:
			logger.error(f"Integrity error while creating win_rate '{player} - {game_mode}': {e}")
			return None
		except DatabaseError as e:
			logger.error(f"Database error while creating win_rate '{player} - {game_mode}': {e}")
			return None
		return None
	
	@classmethod
	def get_win_rate_data(cls, player, game_mode):
		try:
			instance = cls.objects.get(player=player, game_mode=game_mode)
			if instance:
				return {
					'win_rate': instance.win_rate,
					'wins': instance.wins,
					'losses': instance.losses
				}
		except cls.DoesNotExist:
			return {
				'win_rate': None,
				'wins': None,
				'losses': None
			}
		return {
			'win_rate': None,
			'wins': None,
			'losses': None
		}