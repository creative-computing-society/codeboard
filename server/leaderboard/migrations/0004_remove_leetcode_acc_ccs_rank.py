# Generated by Django 5.0.6 on 2024-06-18 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0003_leaderboard_leetcode_acc_daily_rank_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leetcode_acc',
            name='ccs_rank',
        ),
    ]
