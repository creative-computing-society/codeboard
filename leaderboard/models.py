from django.db import models
from django.utils import timezone
from ccs_auth.models import CUser


class Interval(models.TextChoices):
    DAY = "day", "day"
    WEEK = "week", "week"
    MONTH = "month", "month"


class QuestionType(models.TextChoices):
    DAILY = "daily", "daily"
    WEEKLY = "weekly", "weekly"
    MONTHLY = "monthly", "monthly"


class Difficulty(models.TextChoices):
    EASY = "Basic", "Basic"
    MEDIUM = "Intermediate", "Intermediate"
    HARD = "Advanced", "Advanced"


class Leetcode(models.Model):
    user = models.OneToOneField(CUser, on_delete=models.CASCADE, default=None)
    id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=100, null=False, blank=False, unique=True, default=""
    )
    name = models.CharField(max_length=100, null=True, blank=True, default="Scraping..")
    leetcode_rank = models.CharField(
        max_length=10, null=True, blank=True, default="Scraping.."
    )

    daily_rank = models.IntegerField(null=True, blank=True, default=0)
    weekly_rank = models.IntegerField(null=True, blank=True, default=0)
    monthly_rank = models.IntegerField(null=True, blank=True, default=0)

    photo_url = models.URLField(max_length=200, null=True, blank=True, default=None)

    total_solved = models.IntegerField(null=True, blank=True, default=0)
    matched_ques = models.IntegerField(null=True, blank=True, default=0)

    submission_dict = models.JSONField(null=True, blank=True, default=dict)
    total_solved_dict = models.JSONField(null=True, blank=True, default=dict)
    matched_ques_dict = models.JSONField(null=True, blank=True, default=dict)

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class Question(models.Model):
    question_key = models.AutoField(primary_key=True)
    leetcode_id = models.IntegerField(null=False, blank=False, default=0)
    title = models.CharField(max_length=100, null=False, blank=False, default="")
    titleSlug = models.CharField(max_length=100, null=False, blank=False, default="")
    questionDate = models.DateTimeField(blank=False, default=timezone.now)
    difficulty = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        choices=Difficulty.choices,
        default="Basic",
    )

    def __str__(self):
        return self.title


class LeaderboardEntry(models.Model):
    user = models.ForeignKey(Leetcode, on_delete=models.CASCADE, db_index=True)
    interval = models.CharField(
        max_length=10, choices=Interval.choices
    )  # 'day', 'week', 'month'
    questions_solved = models.IntegerField(null=False, default=0)
    earliest_solved_timestamp = models.BigIntegerField(null=False, default=0)

    class Meta:
        unique_together = ("user", "interval")


class Leaderboard(models.Model):
    leaderboard_key = models.AutoField(primary_key=True)
    leaderboard_type = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        choices=QuestionType.choices,
        default="daily",
    )
    leaderboard_data = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.leaderboard_type
