import logging
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from leaderboard.models import Question
from .populateQuestions import populate_question_model
from datetime import datetime, timezone
import pytz

# Define a logger for this module
logger = logging.getLogger(__name__)

CUser = get_user_model()

def admin_login(request):
    try:
        if request.user.is_authenticated:
            return redirect('admin_dash:admin_dashboard')
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_obj = CUser.objects.filter(email=email)
            if not user_obj.exists():
                messages.info(request, 'User not found')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            user_obj = authenticate(email=email, password=password)

            if user_obj and user_obj.is_staff:
                login(request, user_obj, backend='ccs_auth.auth_backends.SSOAuthenticationBackend')
                return redirect('admin_dash:admin_dashboard')
            
            messages.info(request, 'Invalid credentials')
            return redirect('admin_dash:admin_login')
        return render(request, 'admin_dash/login.html')
    except Exception as e:
        logger.error(f"Error during admin login: {e}")
        return redirect('admin_dash:admin_login')
        
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_dash:admin_login')
    all_questions = Question.objects.all()
    return render(request, 'admin_dash/dashboard.html', {'questions': all_questions})

def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('admin_dash:admin_login')

def edit_question(request, question_id, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('admin_dash:admin_login')
    question_obj = Question.objects.filter(pk=question_id).first()
    logger.debug(f"Editing question with ID {question_id}: {question_obj}")
    if not question_obj:
        return redirect('admin_dash:admin_dashboard')
    if request.method == 'POST':
        title = request.POST.get('title')
        titleSlug = request.POST.get('titleSlug')
        difficulty = request.POST.get('difficulty')

        i_datetime = request.POST.get('questionDate')
        datetime_object = datetime.strptime(i_datetime, "%Y-%m-%dT%H:%M")
        datetime_object = datetime_object.replace(tzinfo=pytz.timezone('Asia/Kolkata'))

        question_obj.title = title
        question_obj.titleSlug = titleSlug
        question_obj.difficulty = difficulty
        question_obj.questionDate = datetime_object
        question_obj.save()
        messages.info(request, 'Question updated successfully')
        return render(request, 'admin_dash/edit.html', {'question': question_obj})
    return render(request, 'admin_dash/edit.html', {'question': question_obj})

def add_ques_from_id(request):
    if not request.user.is_authenticated:
        return redirect('admin_dash:admin_login')
    if request.method == 'POST':
        ques_ids = validate_ques_ids(request.POST.get("question_ids"))
        if ques_ids == []:
            messages.info(request, 'Invalid input')
            return redirect('admin_dash:admin_dashboard')
        
        all_ques = True
        for ques in ques_ids:
            if not Question.objects.filter(pk=ques):
                all_ques = False
        if all_ques:
            logger.info(f"Questions with IDs {ques_ids} created successfully.")
        else:
            logger.warning("Not all questions were successfully created.")

    return redirect('admin_dash:admin_dashboard')

def delete_ques_with_ids(request):
    if not request.user.is_authenticated:
        return redirect('admin_dash:admin_login')

    try:
        ques_ids = request.POST.get('selected_questions')  # Match the name of the hidden input
        logger.debug(f"Deleting questions with IDs: {ques_ids}")
        if ques_ids:
            ques_ids_list = ques_ids.split(',')
            for ques in ques_ids_list:
                Question.objects.filter(pk=int(ques)).first().delete()
                if not Question.objects.filter(pk=int(ques)):
                    logger.info(f"Question with ID {ques} was deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting questions: {e}")
    return redirect('admin_dash:admin_dashboard')

def validate_ques_ids(ques_ids):
    try:
        id_list = list(map(int, ques_ids.split(',')))
        
        unique_ids = set()
        for question_id in id_list:
            if Question.objects.filter(pk=question_id).exists():
                logger.info(f"Question with ID {question_id} already exists.")
            else:
                if question_id:
                    populate_question_model(question_id)
                unique_ids.add(question_id)
        
        return list(unique_ids)
    except ValueError:
        logger.error("The input contains invalid IDs. Please provide a comma-separated list of integers.")
        return []