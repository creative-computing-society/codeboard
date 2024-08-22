from django.db import models
from django.contrib.postgres.fields import ArrayField
from ccs_auth.models import CUser
import datetime

class Leetcode(models.Model):
    user = models.OneToOneField(CUser, on_delete=models.CASCADE, null=True, blank=True,default=None )
    id = models.AutoField(primary_key=True)
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
    # question_key = models.AutoField(primary_key=True)
    leetcode_id = models.IntegerField(null=False, blank=False, default=0, primary_key=True, unique=True)
    title = models.CharField(max_length=100, default="")
    titleSlug = models.CharField(max_length=100, default="")
    questionDate = models.DateTimeField(blank=False,default=datetime.datetime.now)
    difficulty = models.CharField(max_length=20, null=False, blank=False, choices=[('Basic', 'Basic'), ('Intermidiate', 'Intermidiate'), ('Advanced', 'Advanced')], default='Basic')
    def __str__(self):
        return self.title
    
class LeaderboardEntry(models.Model):
    user = models.ForeignKey(Leetcode, on_delete=models.CASCADE)
    interval = models.CharField(max_length=10)  # 'day', 'week', 'month'
    questions_solved = models.IntegerField(null=False, default=0)
    earliest_solved_timestamp = models.BigIntegerField(null=False, default=0)

    class Meta:
        unique_together = ('user', 'interval')
    
    def __str__(self):
        return f'{self.user.username} - {self.interval}'

class Leaderboard(models.Model):
    leaderboard_key = models.AutoField(primary_key=True)
    leaderboard_type = models.CharField(max_length=20, null=False, blank=False, choices=[('daily', 'daily'), ('weekly', 'weekly'), ('monthly', 'monthly')], default='daily')
    leaderboard_data = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.leaderboard_type
    
class UsernameChangeRequest(models.Model):
    user = models.ForeignKey(CUser, on_delete=models.CASCADE)
    new_username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    old_username = models.CharField(max_length=100, null=False, blank=False)
    status = models.CharField(max_length=20, null=False, blank=False, choices=[('pending', 'pending'), ('approved', 'approved'), ('rejected', 'rejected')], default='pending')

    def __str__(self):
        return self.new_username