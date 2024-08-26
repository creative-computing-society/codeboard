from django.urls import path
from .views import *

app_name = 'admin_dash'

urlpatterns = [
    path('login/', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/<int:question_id>/edit/', edit_question, name='edit_question'),
    path('dashboard/add_from_id/', add_ques_from_id, name='add_ques_from_id'),
    path('dashboard/delete_questions/', delete_ques_with_ids, name='delete_ques_with_ids'),
]
