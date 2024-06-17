# Generated by Django 5.0.6 on 2024-06-17 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderboardentry',
            name='earliest_solved_timestamp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaderboardentry',
            name='questions_solved',
            field=models.IntegerField(default=0),
        ),
    ]
