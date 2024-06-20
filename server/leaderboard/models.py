from django.db import models
from django.contrib.postgres.fields import ArrayField
import datetime

class leetcode_acc(models.Model):
    user = models.AutoField(primary_key=True, unique=True, default=0)
    username = models.CharField(max_length=100, null=False, blank=False, unique=True, default="")
    name = models.CharField(max_length=100, null=True, blank=True, default="Scraping..")
    leetcode_rank= models.CharField(max_length=10, null=True, blank=True, default="Scraping..")

    daily_rank = models.IntegerField(null=True, blank=True, default=0)
    weekly_rank = models.IntegerField(null=True, blank=True, default=0)
    monthly_rank = models.IntegerField(null=True, blank=True, default=0)

    photo_url = models.CharField(max_length=200, null=True, blank=True, default="Scarping..")

    total_solved = models.IntegerField(null=True, blank=True, default=0)
    matched_ques = models.IntegerField(null=True, blank=True, default=0)

    submission_dict = models.JSONField(null=True, blank=True, default=dict)
    total_solved_dict = models.JSONField(null=True, blank=True, default=dict)
    matched_ques_dict = models.JSONField(null=True, blank=True, default=dict)

    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username

class Question(models.Model):
    question_key = models.AutoField(primary_key=True)
    leetcode_id = models.IntegerField(null=False, blank=False, default=0)
    title = models.CharField(max_length=100, null=False, blank=False, default="")
    titleSlug = models.CharField(max_length=100, null=False, blank=False, default="")
    questionDate = models.DateTimeField(blank=False,default=datetime.datetime.now)
    difficulty = models.CharField(max_length=20, null=False, blank=False, choices=[('Basic', 'Basic'), ('Intermidiate', 'Intermidiate'), ('Advanced', 'Advanced')], default='Basic')
    def __str__(self):
        return self.title
    
class LeaderboardEntry(models.Model):
    user = models.ForeignKey(leetcode_acc, on_delete=models.CASCADE)
    interval = models.CharField(max_length=10)  # 'day', 'week', 'month'
    questions_solved = models.IntegerField(null=False, default=0)
    earliest_solved_timestamp = models.BigIntegerField(null=False, default=0)

    class Meta:
        unique_together = ('user', 'interval')

class Leaderboard(models.Model):
    leaderboard_key = models.AutoField(primary_key=True)
    leaderboard_type = models.CharField(max_length=20, null=False, blank=False, choices=[('daily', 'daily'), ('weekly', 'weekly'), ('monthly', 'monthly')], default='daily')
    leaderboard_data = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.leaderboard_type