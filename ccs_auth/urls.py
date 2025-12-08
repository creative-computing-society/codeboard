from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('google-login/', views.GoogleLoginView.as_view(), name='google-login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register-leetcode/', views.RegisterLeetcode.as_view(), name='register-leetcode'),
    path('verify-leetcode/', views.VerifyLeetcode.as_view(), name='verify-leetcode'),
]
