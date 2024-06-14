from celery import shared_task
from django.utils import timezone
import datetime, time
from .models import *
from .query_manager import *

def get_latest_submissions(submissions):
    latest_submissions = {}
    for submission in submissions:
        question_id = int(submission[0])
        timestamp = int(submission[2])
        if question_id not in latest_submissions or timestamp > latest_submissions[question_id]:
            latest_submissions[question_id] = timestamp
    return latest_submissions

def match_questions(questions_given, latest_solved):
    matched_ques = []
    for question in questions_given:
        question_id = int(question[0])
        question_timestamp = int(question[2])
        if question_id in latest_solved:
            solved_timestamp = latest_solved[question_id]
            print(f"Comparing: question_id={question_id}, question_timestamp={question_timestamp}, solved_timestamp={solved_timestamp}")
            if solved_timestamp > question_timestamp:
                matched_ques.append(question_id)
    return matched_ques

@shared_task(bind=True)
def get_user_data(self, username, user_id):
    limit = 500
    
    # Fetch user-related data
    user_data = send_query(MATCHED_USER_QUERY, {"username": username})['data']['matchedUser']['profile']
    submitted_questions = send_query(QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})['data']['recentAcSubmissionList']
    language_problem_count = send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})['data']['matchedUser']['languageProblemCount']
    all_question_list_var = {
        "categorySlug": "all-code-essentials",
        "skip": 0,
        "limit": 5000,
        "filters": {}
    }
    # Array of all questions, each question has frontendQuestionId and titleSlug
    all_question_list = send_query(ALL_QUESTION_LIST_QUERY, all_question_list_var)['data']['problemsetQuestionList']['questions']
    # Make a map of titleSlug to frontendQuestionId (leetcode_id)
    titleSlug_to_id = {question['titleSlug']: question['frontendQuestionId'] for question in all_question_list}

    # Extract solved questions with timestamps
    ques_solved = [
        [titleSlug_to_id[question['titleSlug']], question['titleSlug'], question['timestamp']]
        for question in submitted_questions if question['titleSlug'] in titleSlug_to_id
    ]

    # Logging to verify ques_solved
    print(f"ques_solved: {ques_solved}")

    # Get the latest submissions for each question ID
    latest_solved = get_latest_submissions(ques_solved)

    # Logging to verify latest_solved
    print(f"latest_solved: {latest_solved}")

    # Fetch given questions and convert dates to timestamps
    questions = Question.objects.all()
    ques_given = [
        [question.leetcode_id, question.titleSlug, time.mktime(question.questionDate.timetuple())]
        for question in questions
    ]

    # Logging to verify ques_given
    print(f"ques_given: {ques_given}")

    # Match questions
    matched_ques = match_questions(ques_given, latest_solved)

    # Logging to verify matched_ques
    print(f"matched_ques: {matched_ques}")

    # Calculate total number of questions solved
    total_solved = sum(question['problemsSolved'] for question in language_problem_count)

    # Update user data in the database
    instance = leetcode_acc.objects.get(user=user_id)
    instance.name = user_data['realName']
    instance.leetcode_rank = user_data['ranking']
    instance.photo_url = user_data['userAvatar']
    instance.total_solved = total_solved
    instance.matched_ques = len(matched_ques)
    instance.total_solved_list = list(latest_solved.keys())  # Corrected to use keys of the dictionary
    instance.matched_ques_list = matched_ques
    instance.save()

    print(f"Data for {username} saved successfully")

@shared_task(bind=True)
def refresh_user_data(self):
    users = leetcode_acc.objects.all()
    if not users:
        return

    for user in users:
        get_user_data.delay(user.username, user.user)

    print("Data refreshed successfully")

@shared_task(bind=True)
def create_leaderboard(self):
    users = leetcode_acc.objects.all().order_by('-matched_ques')
    leaderboard = []
    # 