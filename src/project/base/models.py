import json
import random
import uuid

from IPython.core.display import JSON
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    player_move = models.CharField(max_length=20, choices=GAME_MOVE_CHOICES)
    opponent_move = models.CharField(max_length=20, choices=GAME_MOVE_CHOICES)
    outcome = models.CharField(max_length=20, choices=GAME_RESULT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.player_move} vs {self.opponent_move} - {self.outcome} - {self.game}"

    def get_computer_move(self):
        self.opponent_move = random.choice(list(dict(GAME_MOVE_CHOICES).keys()))

    def play_offline_round(self, class_name, game_id):
        game = Game.objects.get(pk=game_id)
        if not game.score:
            game.score = {'User': 0, 'Computer': 0}
            game.save()
        if game.game_status == COMPLETED:
            return
        else:
            game.rounds_played += 1
            self.round_number = game.rounds_played
            self.player_move = dict(GAME_MOVE_CHOICES)[class_name]
            self.get_computer_move()
            if class_name == self.opponent_move:
                self.outcome = TIE
            elif (class_name == ROCK and self.opponent_move == SCISSORS) or \
                    (class_name == SCISSORS and self.opponent_move == PAPER) or \
                    (class_name == PAPER and self.opponent_move == ROCK):
                self.outcome = WIN
                game.score['User'] += 1
            else:
                self.outcome = LOSE
                game.score['Computer'] += 1

            game.save()
            self.save()
            if game.score['User'] == (game.best_of / 2 + 0.5) or game.score['Computer'] == (game.best_of / 2 + 0.5):
                print(
                    "game.score['User'] == (game.best_of / 2 + 0.5) or game.score['Computer'] == (game.best_of / 2 + 0.5)")
                player = Player.objects.get(user=game.user)
                game.game_status = COMPLETED
                rounds = Round.objects.filter(game=game)
                player_moves = [round.player_move for round in rounds]
                opponent_moves = [round.opponent_move for round in rounds]
                if game.score['User'] > game.score['Computer']:
                    print("game.score['User'] > game.score['Computer']")
                    result = Result.objects.create(game=game, result=WIN, player=player, player_moves=player_moves,
                                                   opponent_moves=opponent_moves)
                    game.result = WIN
                elif game.score['User'] < game.score['Computer']:
                    print("game.score['User'] < game.score['Computer']")
                    result = Result.objects.create(game=game, result=LOSE, player=player, player_moves=player_moves,
                                                   opponent_moves=opponent_moves)
                    game.result = LOSE

                # get the player and update his stats
                player = Player.objects.get(user=game.user)
                player.update_stats(result)
                result.save()
                game.save()
                self.save()


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    room = models.ManyToManyField(Room, related_name='players', null=True, blank=True)
    wins = models.IntegerField(default=0, null=True, blank=True)
    losses = models.IntegerField(default=0, null=True, blank=True)
    games = models.ManyToManyField(Game, related_name='players', null=True, blank=True)
    played_moves = JSONField(default=dict, null=True, blank=True)
    faced_moves = JSONField(default=dict, null=True, blank=True)
    most_played_move = models.CharField(max_length=64, choices=GAME_MOVE_CHOICES, default='', null=True, blank=True)
    most_faced_move = models.CharField(max_length=64, choices=GAME_MOVE_CHOICES, default='', null=True, blank=True)
    win_streak = models.IntegerField(default=0, null=True, blank=True)
    loss_streak = models.IntegerField(default=0, null=True, blank=True)
    win_percentage = models.FloatField(default=0, null=True, blank=True)

    def update_stats(self, result):
        if result.result == WIN:
            self.wins += 1
            self.loss_streak = 0
            self.win_streak += 1
        elif result.result == LOSE:
            self.losses += 1
            self.win_streak = 0
            self.loss_streak += 1

        total_games = self.wins + self.losses
        self.win_percentage = round(self.wins / total_games * 100, 2)

        # update the played_moves field with the moves played in the game
        for move in result.player_moves:
            if move in self.played_moves:
                self.played_moves[move] += 1
            else:
                self.played_moves[move] = 1

        self.most_played_move = max(self.played_moves, key=self.played_moves.get)

        for move in result.opponent_moves:
            if move in self.faced_moves:
                self.faced_moves[move] += 1
            else:
                self.faced_moves[move] = 1

        self.most_faced_move = max(self.faced_moves, key=self.faced_moves.get)

        # update the win_streak and loss_streak fields and the win_percentage field
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

    def __str__(self):
        return f"{self.game} - {self.result}"


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        player = Player.objects.create(user=instance)
        print(player.pk, player._state.db)


post_save.connect(create_player, sender=User)
