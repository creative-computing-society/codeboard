from django.urls import path
from . import views

urlpatterns = [
    path('register_user/', views.RegisterLeetcode.as_view(), name='register_user'),
    path('get_leetcode/', views.GetLeetcodeInfo.as_view(), name='get_leetcode'),
    path('get_user/', views.GetUserInfo.as_view(), name='get_user'),
    path('today_questions/', views.GetQuestionsForTheDay.as_view(), name='today_questions'),
    path('refresh_data/', views.DebugRefreshUserData.as_view(), name='refresh_data'),
    path('daily_leaderboard/', views.DailyLeaderboard.as_view(), name='daily_leaderboard'),
    path('weekly_leaderboard/', views.WeeklyLeaderboard.as_view(), name='weekly_leaderboard'),
    path('monthly_leaderboard/', views.MonthlyLeaderboard.as_view(), name='monthly_leaderboard'),
]
