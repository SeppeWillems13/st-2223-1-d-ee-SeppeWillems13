import json
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Choices for the game_move field
ROCK = 'Rock'
PAPER = 'Paper'
SCISSORS = 'Scissors'
GAME_MOVE_CHOICES = (
    (ROCK, 'Rock'),
    (PAPER, 'Paper'),
    (SCISSORS, 'Scissors'),
)

# Choices for the game_status field
ONGOING = 'Ongoing'
COMPLETED = 'Completed'
ABANDONED = 'Abandoned'
GAME_STATUS_CHOICES = (
    (ONGOING, 'Ongoing'),
    (COMPLETED, 'Completed'),
    (ABANDONED, 'Abandoned'),
)

# Choices for the result field
WIN = 'Win'
LOSE = 'Lose'
TIE = 'Tie'
GAME_RESULT_CHOICES = (
    (WIN, 'Win'),
    (LOSE, 'Lose'),
    (TIE, 'Tie'),
)


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")

    # TODO COMMENT OUT WHEN NEW MIGRATIONS CREATING SUPERUSER
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_rooms', null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=20, blank=True, primary_key=True, unique=True)
    is_online = models.BooleanField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponent', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    game_status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default=ONGOING)
    score = JSONField(default=dict)
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES, null=True)
    best_of = models.IntegerField()
    rounds_played = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.id) + ' - ' + str(self.room) + ' - ' + str(self.user) + ' - ' + str(self.game_status)


class Round(models.Model):
    round_number = models.IntegerField(default=0)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_rounds')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponent_rounds', null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    player_move = models.CharField(max_length=20, choices=GAME_MOVE_CHOICES)
    opponent_move = models.CharField(max_length=20, choices=GAME_MOVE_CHOICES)
    outcome = models.CharField(max_length=20, choices=GAME_RESULT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.player_move} vs {self.opponent_move} - {self.outcome} - {self.game}"


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    wins = models.IntegerField(default=0, null=True, blank=True)
    losses = models.IntegerField(default=0, null=True, blank=True)
    games = models.ManyToManyField(Game, related_name='players', null=True, blank=True)
    default_moves = {"Rock": 0, "Paper": 0, "Scissors": 0}
    played_moves = JSONField(default=default_moves, null=True, blank=True)
    faced_moves = JSONField(default=default_moves, null=True, blank=True)
    most_played_move = models.CharField(max_length=64, choices=GAME_MOVE_CHOICES, default='', null=True, blank=True)
    most_faced_move = models.CharField(max_length=64, choices=GAME_MOVE_CHOICES, default='', null=True, blank=True)
    win_streak = models.IntegerField(default=0, null=True, blank=True)
    loss_streak = models.IntegerField(default=0, null=True, blank=True)
    win_percentage = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_most_faced_move(self):
        self.faced_moves = json.loads(self.faced_moves)
        return max(self.faced_moves, key=self.faced_moves.get)

    def get_most_played_move(self):
        self.played_moves = json.loads(self.played_moves)
        return max(self.played_moves, key=self.played_moves.get)

    class Meta:
        ordering = ['user__username']


class Result(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    player_moves = JSONField(default=dict)
    opponent_moves = JSONField(default=dict)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.game} - {self.result}"


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


post_save.connect(create_player, sender=User)
