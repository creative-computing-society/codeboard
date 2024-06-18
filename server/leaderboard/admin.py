from django.contrib import admin
from django.db.models import Case, When, Value, IntegerField
from leaderboard.models import *

class RankFilter(admin.SimpleListFilter):
    title = 'Monthly Rank'
    parameter_name = 'monthly_rank'

    def lookups(self, request, model_admin):
        return (
            ('non_zero', 'Non-zero Ranks'),
            ('zero', 'Zero Ranks'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'non_zero':
            return queryset.exclude(monthly_rank=0).order_by('monthly_rank')
        if self.value() == 'zero':
            return queryset.filter(monthly_rank=0)
        # Default ordering: non-zero ranks in ascending order, followed by zero ranks
        return queryset.annotate(
            custom_order=Case(
                When(monthly_rank=0, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('custom_order', 'monthly_rank')

class LeetcodeAdmin(admin.ModelAdmin):
    list_display = ('username', 'monthly_rank', 'matched_ques')
    list_filter = (RankFilter,)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('leetcode_id', 'title', 'questionDate','difficulty')
    list_filter = ('questionDate', 'difficulty')

admin.site.register(leetcode_acc, LeetcodeAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(LeaderboardEntry)
admin.site.register(Leaderboard)