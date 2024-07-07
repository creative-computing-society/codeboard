from django.urls import path
from . import views

urlpatterns = [
    path('refresh_data/', views.DebugRefreshUserData.as_view(), name='refresh_data'),

    # POST
    # path('register/', views.Register.as_view(), name='register'),

    # GET
    path('user/profile/', views.Profile.as_view(), name='profile'),
    path('questions/today/', views.GetQuestionsForTheDay.as_view(), name='today_questions'),
    path('questions/all/', views.GetAllQuestions.as_view(), name='all_questions'),
    path('daily/', views.DailyLeaderboard.as_view(), name='daily_leaderboard'),
    path('weekly/', views.WeeklyLeaderboard.as_view(), name='weekly_leaderboard'),
    path('monthly/', views.MonthlyLeaderboard.as_view(), name='monthly_leaderboard'),
]
