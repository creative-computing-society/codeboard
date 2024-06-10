from django.contrib import admin
from leaderboard.models import leetcode_acc, Question

class LeetcodeAdmin(admin.ModelAdmin):
    list_display = ('leetcode_name', 'rank', 'number_of_questions')

admin.site.register(leetcode_acc)
admin.site.register(Question)
