from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUPView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('test_token/', views.TestToken.as_view(), name='test_token'),
    path('signup_token/', views.SignUpTokenView.as_view(), name='signup_token'),
]
