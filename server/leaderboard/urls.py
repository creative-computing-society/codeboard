from django.urls import path, include
from . import views

urlpatterns = [
    path('register_user/', views.register_leetcode.as_view(), name='register_user'),
    path('get_leetcode/', views.getLeetcodeInfo.as_view(), name='get_leetcode'),
    path('get_user/', views.getUserInfo.as_view(), name='get_user'),
    path('get_question_id/', views.getQuestionID.as_view(), name='get_question_id'),
]


