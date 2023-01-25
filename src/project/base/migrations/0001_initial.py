# Generated by Django 4.1.5 on 2023-01-25 01:18

import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                              help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                              max_length=150, unique=True,
                                              validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                                              verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.',
                                                 verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True,
                                                  help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=200, null=True)),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('avatar', models.ImageField(default='avatar.svg', null=True, upload_to='')),
                ('groups', models.ManyToManyField(blank=True,
                                                  help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user', to='auth.group',
                                                  verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user',
                                                            to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('game_status', models.CharField(
                    choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed'), ('Abandoned', 'Abandoned')],
                    default='Ongoing', max_length=10)),
                ('score', models.JSONField(default=dict)),
                ('result', models.CharField(choices=[('Win', 'Win'), ('Lose', 'Lose'), ('Tie', 'Tie')], max_length=10,
                                            null=True)),
                ('best_of', models.IntegerField()),
                ('rounds_played', models.IntegerField(default=0)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('opponent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                               related_name='opponent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False,
                                      to=settings.AUTH_USER_MODEL)),
                ('wins', models.IntegerField(blank=True, default=0, null=True)),
                ('losses', models.IntegerField(blank=True, default=0, null=True)),
                ('played_moves',
                 models.JSONField(blank=True, default={'Paper': 0, 'Rock': 0, 'Scissors': 0}, null=True)),
                (
                'faced_moves', models.JSONField(blank=True, default={'Paper': 0, 'Rock': 0, 'Scissors': 0}, null=True)),
                ('most_played_move',
                 models.CharField(blank=True, choices=[('Rock', 'Rock'), ('Paper', 'Paper'), ('Scissors', 'Scissors')],
                                  default='', max_length=64, null=True)),
                ('most_faced_move',
                 models.CharField(blank=True, choices=[('Rock', 'Rock'), ('Paper', 'Paper'), ('Scissors', 'Scissors')],
                                  default='', max_length=64, null=True)),
                ('win_streak', models.IntegerField(blank=True, default=0, null=True)),
                ('loss_streak', models.IntegerField(blank=True, default=0, null=True)),
                ('win_percentage', models.FloatField(blank=True, default=0, null=True)),
            ],
            options={
                'ordering': ['user__username'],
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField(default=0)),
                ('player_move',
                 models.CharField(choices=[('Rock', 'Rock'), ('Paper', 'Paper'), ('Scissors', 'Scissors')],
                                  max_length=20)),
                ('opponent_move',
                 models.CharField(choices=[('Rock', 'Rock'), ('Paper', 'Paper'), ('Scissors', 'Scissors')],
                                  max_length=20)),
                (
                'outcome', models.CharField(choices=[('Win', 'Win'), ('Lose', 'Lose'), ('Tie', 'Tie')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('game',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='base.game')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host_rounds',
                                           to=settings.AUTH_USER_MODEL)),
                ('opponent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                               related_name='opponent_rounds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('name', models.CharField(blank=True, max_length=200)),
                ('code', models.CharField(blank=True, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('is_online', models.BooleanField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_rooms',
                                           to=settings.AUTH_USER_MODEL)),
                ('opponent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                               related_name='joined_rooms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.AddField(
            model_name='game',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.room'),
        ),
        migrations.AddField(
            model_name='game',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(choices=[('Win', 'Win'), ('Lose', 'Lose'), ('Tie', 'Tie')], max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('player_moves', models.JSONField(default=dict)),
                ('opponent_moves', models.JSONField(default=dict)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results',
                                           to='base.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.player')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AddField(
            model_name='player',
            name='games',
            field=models.ManyToManyField(blank=True, null=True, related_name='players', to='base.game'),
        ),
    ]
