from django.db import models
from django.contrib.postgres.fields import ArrayField

class leetcode_acc(models.Model):
    # user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='leetcode')
    user = models.AutoField(primary_key=True)
    leetcode_name = models.CharField(max_length=100, null=False, blank=False, unique=True, default="")
    name = models.CharField(max_length=100, null=True, blank=True, default="Scraping..")
    leetcode_rank= models.CharField(max_length=10, null=True, blank=True, default="Scraping..")
    ccs_rank = models.IntegerField(null=True, blank=True, default=0)
    photo_url = models.CharField(max_length=200, null=True, blank=True, default="Scarping..")
    total_solved = models.IntegerField(null=True, blank=True, default=0)
    matched_ques = models.IntegerField(null=True, blank=True, default=0)
    total_solved_list = ArrayField(models.IntegerField(unique=True), default=list, blank=True)
    matched_ques_list = ArrayField(models.IntegerField(unique=True), default=list, blank=True)
    def __str__(self):
        return self.leetcode_name

class Question(models.Model):
    question_key = models.AutoField(primary_key=True)
    leetcode_id = models.IntegerField(null=False, blank=False, default=0)
    title = models.CharField(max_length=100, null=False, blank=False, default="")
    titleSlug = models.CharField(max_length=100, null=False, blank=False, default="")
    difficulty = models.CharField(max_length=20, null=False, blank=False, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Easy')
    def __str__(self):
        return self.title