from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Room(models.Model):
    # Choices for the room type field
    ROOM_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=User)
    players = models.ManyToManyField(User, related_name='players', blank=True)
    name = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=20, blank=True)
    room_type = models.CharField(max_length=200, choices=ROOM_TYPE_CHOICES, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


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
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


post_save.connect(create_player, sender=User)