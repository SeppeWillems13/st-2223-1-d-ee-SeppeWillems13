# Generated by Django 4.1.5 on 2023-01-18 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='game_move',
            new_name='player_move',
        ),
    ]
