from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import leetcode_acc, LeaderboardEntry, Question
from .query_manager import *
import time
from pprint import pprint

def get_latest_submissions(submissions):
    latest_submissions = {}
    for submission in submissions:
        question_id = int(submission[0])
        timestamp = int(submission[2])
        if question_id not in latest_submissions or timestamp > latest_submissions[question_id]:
            latest_submissions[question_id] = timestamp
    return latest_submissions

def match_questions_to_solved(questions, solved_submissions: dict):
    matched_ques: dict = {}
    for question in questions:
        question_id = int(question[0])
        question_timestamp = int(question[2])
        if question_id in solved_submissions.keys():
            solved_timestamp = solved_submissions[question_id]
            if solved_timestamp > question_timestamp:
                matched_ques[question_id] = solved_timestamp
    return matched_ques

def cal_solved_intervals(questions, solved_dict: dict):
    current_time = timezone.now()
    one_day_interval = current_time - timedelta(days=1)
    one_week_interval = current_time - timedelta(weeks=1)
    one_month_interval = current_time - timedelta(days=30)  # Approximation for a month

    solved_within_one_day = {}
    solved_within_one_week = {}
    solved_within_one_month = {}
    

    for question in questions:
        question_id = int(question[0])
        question_timestamp = int(question[2])
        if str(question_id) in solved_dict:
            ques_solved_timestamp = solved_dict[str(question_id)]
            if ques_solved_timestamp < question_timestamp:
                print(f"Question: {question_id} - Solved before creation")
                continue  # Skip if question was solved before it was created

            if ques_solved_timestamp >= one_day_interval.timestamp():
                solved_within_one_day[question_id] = ques_solved_timestamp
                print(f"Question: {question_id} - Solved within one day")
            
            if ques_solved_timestamp >= one_week_interval.timestamp():
                solved_within_one_week[question_id] = ques_solved_timestamp
                print(f"Question: {question_id} - Solved within one week")

            if ques_solved_timestamp >= one_month_interval.timestamp():
                solved_within_one_month[question_id] = ques_solved_timestamp
                print(f"Question: {question_id} - Solved within one month")
        else:
            print(f"Question: {question_id} - Not solved")

    return solved_within_one_day, solved_within_one_week, solved_within_one_month

def fetch_user_profile(username):
    return send_query(MATCHED_USER_QUERY, {"username": username})['data']['matchedUser']['profile']

def fetch_submitted_questions(username, limit=500):
    return send_query(QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})['data']['recentAcSubmissionList']

def fetch_language_problem_count(username):
    return send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})['data']['matchedUser']['languageProblemCount']

def fetch_all_questions():
    query_vars = {"categorySlug": "all-code-essentials", "skip": 0, "limit": 5000, "filters": {}}
    return send_query(ALL_QUESTION_LIST_QUERY, query_vars)['data']['problemsetQuestionList']['questions']

def get_or_create_user_instance(user_id):
    return leetcode_acc.objects.get_or_create(user=user_id)

def update_user_instance(instance: leetcode_acc, user_data, matched_questions, latest_solved, total_solved, language_problem_count):
    instance.name = user_data['realName']
    instance.leetcode_rank = user_data['ranking']
    instance.photo_url = user_data['userAvatar']
    instance.total_solved = sum(question['problemsSolved'] for question in language_problem_count)
    instance.matched_ques = len(list(matched_questions.keys()))
    instance.submission_dict = latest_solved
    instance.matched_ques_dict = matched_questions
    instance.total_solved_dict = total_solved
    instance.save()

def process_submissions(submitted_questions, all_question_list):
    titleSlug_to_id = {question['titleSlug']: question['frontendQuestionId'] for question in all_question_list}
    return [
        [titleSlug_to_id[question['titleSlug']], question['titleSlug'], question['timestamp']]
        for question in submitted_questions if question['titleSlug'] in titleSlug_to_id
    ] # [leetcode_id, titleSlug, timestamp]

def generate_leaderboards_entries():
    questions = Question.objects.all()
    ques_given = [
        [question.leetcode_id, question.titleSlug, time.mktime(question.questionDate.timetuple())]
        for question in questions
    ]
    user_instances = leetcode_acc.objects.all()
    for user_instance in user_instances:
        username = user_instance.username
        solved_dict = user_instance.total_solved_dict
        solved_within_one_day, solved_within_one_week, solved_within_one_month = cal_solved_intervals(ques_given, solved_dict)
        if username == 'singlaishan69':
            print(f"user: {username} - Solved_dict: {solved_dict}")
        # print(f"User: {username} - Day: {len(solved_within_one_day)} - Week: {len(solved_within_one_week)} - Month: {len(solved_within_one_month)}")
        daily_entry, _ = LeaderboardEntry.objects.get_or_create(user=user_instance, interval='day')
        weekly_entry, _ = LeaderboardEntry.objects.get_or_create(user=user_instance, interval='week')
        monthly_entry, _ = LeaderboardEntry.objects.get_or_create(user=user_instance, interval='month')

        daily_entry.questions_solved = len(solved_within_one_day)
        weekly_entry.questions_solved = len(solved_within_one_week)
        monthly_entry.questions_solved = len(solved_within_one_month)

        daily_entry.earliest_solved_timestamp = max(solved_within_one_day.values(), default=0)
        weekly_entry.earliest_solved_timestamp = max(solved_within_one_week.values(), default=0)
        monthly_entry.earliest_solved_timestamp = max(solved_within_one_month.values(), default=0)

        daily_entry.save()
        weekly_entry.save()
        monthly_entry.save()
    print("Leaderboard entries generated successfully")

@shared_task(bind=True)
def calculate_leaderboards(self):
    generate_leaderboards_entries()
    one_day, one_week, one_month = {}, {}, {}
    daily, weekly, monthly = [], [], []

    users = leetcode_acc.objects.all()
    for user in users:
        daily_entry = LeaderboardEntry.objects.get(user=user, interval='day')
        weekly_entry = LeaderboardEntry.objects.get(user=user, interval='week')
        monthly_entry = LeaderboardEntry.objects.get(user=user, interval='month')
        daily.append([user.username, daily_entry.questions_solved, daily_entry.earliest_solved_timestamp])
        weekly.append([user.username, weekly_entry.questions_solved, weekly_entry.earliest_solved_timestamp])
        monthly.append([user.username, monthly_entry.questions_solved, monthly_entry.earliest_solved_timestamp])
    
    daily.sort(key=lambda x: (-x[1], x[2]))
    weekly.sort(key=lambda x: (-x[1], x[2]))
    monthly.sort(key=lambda x: (-x[1], x[2]))
    # convert timestamp to human readable format
    for user in daily:
        user[2] = timezone.datetime.fromtimestamp(user[2]).strftime('%Y-%m-%d %H:%M:%S')
    for user in weekly:
        user[2] = timezone.datetime.fromtimestamp(user[2]).strftime('%Y-%m-%d %H:%M:%S')
    for user in monthly:
        user[2] = timezone.datetime.fromtimestamp(user[2]).strftime('%Y-%m-%d %H:%M:%S')

    for idx, user in enumerate(daily):
        one_day[idx+1] =  {"Username": user[0], "Questions Solved": user[1], "Last Solved": user[2]}
    for idx, user in enumerate(weekly):
        one_week[idx+1] =  {"Username": user[0], "Questions Solved": user[1], "Last Solved": user[2]}
    for idx, user in enumerate(monthly):
        one_month[idx+1] =  {"Username": user[0], "Questions Solved": user[1], "Last Solved": user[2]}
    print("Leaderboards calculated successfully")
    return one_day, one_week, one_month

@shared_task(bind=True)
def get_user_data(self, username, user_id):
    user_profile = fetch_user_profile(username)    

    submitted_questions = fetch_submitted_questions(username)
    language_problem_count = fetch_language_problem_count(username)
    all_question_list = fetch_all_questions()

    submissions = process_submissions(submitted_questions, all_question_list)
    latest_solved = get_latest_submissions(submissions)

    user_instance, _ = get_or_create_user_instance(user_id)
    total_solved = user_instance.total_solved_dict
    
    for ques in latest_solved.keys():
        if ques not in total_solved:
            total_solved[ques] = latest_solved[ques]
            
    questions = Question.objects.all()
    ques_given = [
        [question.leetcode_id, question.titleSlug, time.mktime(question.questionDate.timetuple())]
        for question in questions
    ]

    matched_ques = match_questions_to_solved(ques_given, total_solved)
    update_user_instance(user_instance, user_profile, matched_ques, latest_solved, total_solved, language_problem_count)
    
    print(f"Data for {username} saved successfully")

@shared_task(bind=True)
def refresh_user_data(self):
    users = leetcode_acc.objects.all()
    if not users:
        return

    for user in users:
        get_user_data.delay(user.username, user.user)

    print("Data refreshed successfully")
