from django.db import models

class leetcode_acc(models.Model):
    # user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='leetcode')
    user = models.AutoField(primary_key=True)
    leetcode_name = models.CharField(max_length=100, null=False, blank=False, unique=True, default="")
    name = models.CharField(max_length=100, null=True, blank=True, default="Scraping..")
    rank= models.CharField(max_length=10, null=True, blank=True, default="Scraping..")
    photo_url = models.CharField(max_length=200, null=True, blank=True, default="Scarping..")
    number_of_questions = models.IntegerField(null=True, blank=True, default=0)
    last_solved = models.CharField(max_length=50, null=True, blank=True, default="Scraping..")
    
    def __str__(self):
        return self.leetcode_name