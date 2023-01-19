import json
import random
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField
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
    avatar = models.ImageField(null=True, default="avatar.svg")

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
    player_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES)
    opponent_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES)
    game_status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default=ONGOING)
    score = models.TextField(default='{"player1": 0, "player2": 0}')
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES, null=True)
    best_of = models.IntegerField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    player_moves = JSONField(default=dict)
    opponent_moves = JSONField(default=dict)

    def get_computer_move(self):
        self.opponent_move = random.choice(list(dict(GAME_MOVE_CHOICES).keys()))

    def play_offline_game(self, class_name):
        self.player_move = dict(GAME_MOVE_CHOICES)[class_name]
        self.get_computer_move()
        self.player_moves.update({self.player_move: self.player_moves.get(self.player_move, 0) + 1})
        self.opponent_moves.update({self.opponent_move: self.opponent_moves.get(self.opponent_move, 0) + 1})
        score = json.loads(self.score)
        if class_name == self.opponent_move:
            self.result = TIE
        elif (class_name == ROCK and self.opponent_move == SCISSORS) or \
                (class_name == SCISSORS and self.opponent_move == PAPER) or \
                (class_name == PAPER and self.opponent_move == ROCK):
            self.result = WIN
            score['player1'] += 1
        else:
            self.result = LOSE
            score['player2'] += 1
        self.score = json.dumps(score)
        if score['player1'] >= int(self.best_of / 2 + 1) or score['player2'] >= int(self.best_of / 2 + 1):
            self.game_status = COMPLETED
            # Create a new Result object when the game is ended
            player_result = WIN if score['player1'] >= (self.best_of / 2 + 1) else LOSE
            player = Player.objects.get(user=self.user)
            Result.objects.create(player=player, game=self, result=player_result, player_moves=self.player_moves,opponent_moves=self.opponent_moves)
            player.update_stats(player_result, self.player_move, self.opponent_move)
        else:
            self.game_status = ONGOING
        self.updated = timezone.now()
        self.save()

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.room) + ' - ' + str(self.user) + ' - ' + str(self.game_status)


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    room = models.ManyToManyField(Room, related_name='players', null=True, blank=True)
    wins = models.IntegerField(default=0, null=True, blank=True)
    draws = models.IntegerField(default=0, null=True, blank=True)
    losses = models.IntegerField(default=0, null=True, blank=True)
    favorite_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES, null=True, blank=True)
    most_played_move = JSONField(default=dict, null=True, blank=True)
    most_faced_move = JSONField(default=dict, null=True, blank=True)

    def update_stats(self, result, player_move, computer_move):
        if result == WIN:
            self.wins += 1
        elif result == LOSE:
            self.losses += 1
        else:
            self.draws += 1

        if player_move in self.most_played_move:
            self.most_played_move[player_move] += 1
        else:
            self.most_played_move[player_move] = 1

        if computer_move in self.most_faced_move:
            self.most_faced_move[computer_move] += 1
        else:
            self.most_faced_move[computer_move] = 1

        if not self.favorite_move:
            self.favorite_move = player_move
        elif self.most_played_move[player_move] > self.most_played_move[self.favorite_move]:
            self.favorite_move = player_move
        self.save()

    def __str__(self):
        return self.user.username

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


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        player = Player.objects.create(user=instance)
        print(player.pk, player._state.db)


post_save.connect(create_player, sender=User)
