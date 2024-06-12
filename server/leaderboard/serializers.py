from rest_framework import serializers
from .models import leetcode_acc

class leetcode_accSerializer(serializers.ModelSerializer):
    class Meta:
        model = leetcode_acc
        fields = ['leetcode_name', 'name','leetcode_rank', 'ccs_rank', 'photo_url', 'total_solved', 'matched_ques', 'total_solved_list', 'matched_ques_list']