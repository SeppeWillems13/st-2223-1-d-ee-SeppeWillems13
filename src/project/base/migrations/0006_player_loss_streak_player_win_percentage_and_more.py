# Generated by Django 4.1.5 on 2023-01-20 13:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0005_player_faced_moves_player_played_moves_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='loss_streak',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='win_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='win_streak',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
