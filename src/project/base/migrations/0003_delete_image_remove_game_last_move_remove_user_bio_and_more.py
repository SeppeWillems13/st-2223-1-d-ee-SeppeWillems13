# Generated by Django 4.1.5 on 2023-01-19 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_rename_game_move_game_player_move'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.RemoveField(
            model_name='game',
            name='last_move',
        ),
        migrations.RemoveField(
            model_name='user',
            name='bio',
        ),
        migrations.AddField(
            model_name='player',
            name='most_faced_move',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='player',
            name='most_lost_move',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='player',
            name='most_played_move',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='player',
            name='most_won_move',
            field=models.JSONField(default=dict),
        ),
    ]
