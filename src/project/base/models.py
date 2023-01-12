from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    REQUIRED_FIELDS = []


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


class PlayerManager(models.Manager):
    def create_player(self, user, room, is_host=False):
        if not User.objects.filter(pk=user.pk).exists():
            raise ValueError('User does not exist')
        if room.players.count() >= 2 and not room.online:
            raise ValueError('Room is full')
        player = self.create(user=user, room=room, is_host=is_host)
        room.players.add(player)
        return player


class Game(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    game_move = models.CharField(max_length=10, choices=GAME_MOVE_CHOICES)
    game_status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='ongoing')
    result = models.CharField(max_length=10, choices=GAME_RESULT_CHOICES, null=True)
    last_move = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.game_move


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players', null=True, blank=True)
    is_host = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'room',)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


post_save.connect(create_player, sender=User)
