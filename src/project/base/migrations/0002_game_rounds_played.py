# Generated by Django 4.1.5 on 2023-01-19 16:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='rounds_played',
            field=models.IntegerField(default=0),
        ),
    ]
