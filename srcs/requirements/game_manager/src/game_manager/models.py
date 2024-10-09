from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Player(models.Model):
	username = models.CharField(max_length=100, unique=True)  # Nom d'utilisateur unique
	games = models.JSONField(default=dict)  # Dictionnaire pour stocker les parties par mode de jeu

	def __str__(self):
		return self.username

	def add_game(self, game_id, game_mode):
		"""Ajoute un game_id à l'historique du joueur dans le bon mode de jeu."""
		if game_mode not in self.games:
			self.games[game_mode] = []
		self.games[game_mode].append(game_id)
		self.save()  # Sauvegarde les modifications au joueur

class GameInstance(models.Model):
	STATUS_CHOICES = [
		('waiting', 'Waiting for players'),
		('in_progress', 'Game in progress'),
		('aborted', 'Game aborted'),
		('finished', 'Game finished'),
	]

	game_id = models.CharField(max_length=100, unique=True)  # ID de la partie
	usernames = models.JSONField()  # Tableau avec les usernames des joueurs
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')  # Statut de la partie
	scores = models.JSONField(default=dict)  # Dictionnaire des scores par équipe
	winner = models.IntegerField(blank=True, null=True)  # Vainqueur (team) s'il y en a un
	game_duration = models.DurationField(blank=True, null=True)  # Durée de la partie
	game_date = models.DateTimeField(default=timezone.now)  # Date de la partie
	game_mode = models.CharField(max_length=20)  # Mode de jeu

	def __str__(self):
		return f"Game {self.game_id} - Status: {self.status} - Mode: {self.game_mode}"

	def is_finished(self):
		"""Vérifie si la partie est terminée."""
		return self.status == 'finished'

	def clean(self):
		"""Validation pour l'unicité des usernames."""
		if len(self.usernames) != len(set(self.usernames)):
			raise ValidationError("Usernames must be unique.")

	def save(self, *args, **kwargs):
		self.clean()  # Appeler la validation avant de sauvegarder
		super(GameInstance, self).save(*args, **kwargs)

	def update_score(self, team, score):
		"""Met à jour le score de l'équipe spécifiée."""
		self.scores[team] = score
		self.save()  # Sauvegarde les modifications

	def set_winner(self, team):
		"""Définit l'équipe gagnante."""
		self.winner = team
		self.status = 'finished'  # Mettre à jour le statut de la partie
		self.save()  # Sauvegarde les modifications
