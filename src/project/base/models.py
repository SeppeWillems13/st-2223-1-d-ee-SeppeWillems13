import json
import random
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    name = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=20, blank=True, primary_key=True, unique=True)
    online = models.BooleanField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    game_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES)
    game_status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default=ONGOING)
    score = models.TextField(default='{"player1": 0, "player2": 0}')
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES, null=True)
    last_move = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    best_of = models.IntegerField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def play_offline_game(self, class_name):
        class_name = dict(GAME_MOVE_CHOICES)[class_name]
        computer_move = random.choice(list(dict(GAME_MOVE_CHOICES).keys()))
        score = json.loads(self.score)
        if class_name == computer_move:
            self.result = 'TIE'
        elif (class_name == 'rock' and computer_move == 'scissors') or (
                class_name == 'scissors' and computer_move == 'paper') or (
                class_name == 'paper' and computer_move == 'rock'):
            self.result = 'WIN'
            score['player1'] += 1
        else:
            self.result = 'LOSS'
            score['player2'] += 1
        self.score = json.dumps(score)
        if score['player1'] >= (self.best_of / 2 + 1) or score['player2'] >= (self.best_of / 2 + 1):
            self.game_status = 'ENDED'
        else:
            self.game_status = 'ONGOING'
        self.game_move = class_name
        self.updated = timezone.now()
        self.save()

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.game_move


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    room = models.ManyToManyField(Room, related_name='players', blank=True)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    favorite_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['user__username']


class Result(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']


class Image(models.Model):
    username = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images')


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        player = Player.objects.create(user=instance)
        print(player.pk, player._state.db)


post_save.connect(create_player, sender=User)
