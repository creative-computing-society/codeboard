from rest_framework import serializers
from django.utils import timezone
from .models import Leetcode, Question


class LeetCodeSerializer(serializers.ModelSerializer):
    submissions = serializers.SerializerMethodField()

    class Meta:
        model = Leetcode
        fields = [
            "username",
            "name",
            "leetcode_rank",
            "daily_rank",
            "weekly_rank",
            "monthly_rank",
            "photo_url",
            "submissions",
        ]

    def get_submissions(self, obj):
        submission_dict = obj.submission_dict
        # Change the values, which are time stamps to readable format
        for key, value in submission_dict.items():
            submission_dict[key] = timezone.datetime.fromtimestamp(value).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        return submission_dict


class QuestionSerializer(serializers.ModelSerializer):
    leetcode_link = serializers.SerializerMethodField()
    questionDate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "leetcode_id",
            "title",
            "leetcode_link",
            "questionDate",
            "difficulty",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        leetcode_acc_instance = self.context.get("leetcode_acc_instance")
        if leetcode_acc_instance:
            self.solved_set = set(
                map(int, leetcode_acc_instance.matched_ques_dict.keys())
            )
        else:
            self.solved_set = None

    def get_leetcode_link(self, obj):
        return f"https://leetcode.com/problems/{obj.titleSlug}/"

    def get_questionDate(self, obj):
        return obj.questionDate.date()

    def get_status(self, obj):
        if self.solved_set is None:
            return "Account does not exist"
        return (
            "Solved" if obj.leetcode_id in self.solved_set else "Not Solved"
        )  # Apparently this is NOT O(N), shook me
