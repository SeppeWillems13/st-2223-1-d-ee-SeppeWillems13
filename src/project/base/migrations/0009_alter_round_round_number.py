# Generated by Django 4.1.5 on 2023-01-20 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_round_round_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='round_number',
            field=models.IntegerField(default=0),
        ),
    ]
