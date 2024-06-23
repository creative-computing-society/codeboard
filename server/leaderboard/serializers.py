from rest_framework import serializers
from django.utils import timezone
from .models import *

class LeetCodeSerializer(serializers.ModelSerializer):
    submissions = serializers.SerializerMethodField()
    class Meta:
        model = Leetcode
        fields = ['username', 'name','leetcode_rank', 'daily_rank','weekly_rank','monthly_rank', 'photo_url', 'submissions']

    def get_submissions(self, obj):
        submission_dict = obj.submission_dict
        # Change the values, which are time stamps to readable format
        for key, value in submission_dict.items():
            submission_dict[key] = timezone.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        return submission_dict


class QuestionSerializer(serializers.ModelSerializer):
    leetcode_link = serializers.SerializerMethodField()
    questionDate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['leetcode_id', 'title', 'leetcode_link','questionDate', 'difficulty', 'status']

    def get_leetcode_link(self, obj):
        return f"https://leetcode.com/problems/{obj.titleSlug}/"
    
    def get_questionDate(self, obj):
        # Keep only the date part
        return obj.questionDate.date()
    
    def get_status(self, obj):
        leetcode_acc_user = self.context.get('username')

        if leetcode_acc_user is None:
            return "Account ID not provided"
        
        try:
            leetcode_acc_instance = Leetcode.objects.get(username=leetcode_acc_user)
            if obj.leetcode_id in leetcode_acc_instance.matched_ques_list:
                return "Solved"
            else:
                return "Not Solved"
        except Leetcode.DoesNotExist:
            return "Account does not exist"