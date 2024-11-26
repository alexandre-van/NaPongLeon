from django.db import models
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.utils import timezone
from .utils.logger import logger

class Player(models.Model):
	STATUS_CHOICES = [
		('inactive', 'Player is inactive or not engaged in any activity'),
		('in_queue', 'Player is in a matchmaking queue'),
		('pending', 'Player is expected to join a game'),
		('waiting_for_players', 'Player is waiting for other players to join the game'),
		('loading_game', 'Player is waiting for the game to load'),
		('in_game', 'Player is currently playing in a game'),
		('spectate', 'Player is currently spectating a game'),
		('in_private_room', 'Player is currently in a private room'),
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
			logger.warning(f"Player account '{username}' does not exist.")
			return None
		except IntegrityError as e:
			logger.error(f"Integrity error while fetching player '{username}': {e}")
			return None
		except DatabaseError as e:
			logger.exception(f"Unexpected database error while fetching player '{username}': {e}")
			return None

	def update_status(self, new_status):
		if new_status in dict(self.STATUS_CHOICES):
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



class GameInstance(models.Model):
	STATUS_CHOICES = [
		('waiting', 'Waiting for players to join'),
		('loading', 'Players are loading game assets and configurations'),
		('in_progress', 'Game currently in progress'),
		('aborted', 'Game has been aborted'),
		('finished', 'Game has finished'),
	]

	game_id = models.CharField(max_length=100, unique=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
	winner = models.CharField(max_length=20, blank=True, null=True)
	game_date = models.DateTimeField(default=timezone.now)
	game_mode = models.CharField(max_length=30)

	def __str__(self):
		return f"Game {self.game_id} - Status: {self.status} - Mode: {self.game_mode}"

	def is_finished(self):
		return self.status in ['finished', 'aborted']

	def update_status(self, new_status):
		if new_status in dict(self.STATUS_CHOICES):
			self.status = new_status
			self.save()
		else:
			raise ValueError(f"Invalid status: {new_status}")

	def set_winner(self, team):
		self.winner = team
		self.save()

	def abort_game(self):
		self.status = 'aborted'
		self.save()

	def update_score(self, team, score):
		game_score, created = GameScore.objects.get_or_create(game=self, team_name=team)
		game_score.score = score
		game_score.save()

	def add_player_to_team(self, player_username, team_name):
		player = Player.objects.get(username=player_username)  # Fetch the player instance by username
		game_player, created = GamePlayer.objects.get_or_create(game=self, player=player, team_name=team_name)
		if not created:
			logger.debug(f"Player {player.username} is already part of the game {self.game_id}.")



	def clean(self):
		"""Validation pour l'unicité des usernames."""
		usernames = GamePlayer.objects.filter(game=self).values_list('player__username', flat=True)
		if len(usernames) != len(set(usernames)):
			raise ValidationError("Usernames must be unique.")

	def save(self, *args, **kwargs):
		self.clean()  # Appeler la validation avant de sauvegarder
		super(GameInstance, self).save(*args, **kwargs)

	@classmethod
	def create_game(cls, game_id, game_mode, usernames):
		try:
			# Créer l'instance de jeu
			new_game = cls(
				game_id=game_id,
				status='waiting',
				winner=None,
				game_mode=game_mode
			)
			new_game.save()

			# Ajouter chaque joueur au jeu et à l'historique
			for username in usernames:
				player = Player.get_player(username)
				if player:
					PlayerGameHistory.objects.get_or_create(player=player, game=new_game)

			return new_game
		except IntegrityError as e:
			logger.error(f"Integrity error while creating game: {e}")
			return None
		except DatabaseError as e:
			logger.error(f"Database error while creating game: {e}")
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
	team_name = models.CharField(max_length=20)

	class Meta:
		unique_together = ('game', 'player')

class GameScore(models.Model):
	game = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
	team_name = models.CharField(max_length=20)
	score = models.IntegerField(default=0)

	class Meta:
		unique_together = ('game', 'team_name')

