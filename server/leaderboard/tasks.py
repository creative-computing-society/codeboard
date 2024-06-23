from celery import shared_task, group
from django.utils import timezone
from datetime import timedelta
from .models import Leetcode, LeaderboardEntry, Question, Leaderboard
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
    try:
        response = send_query(MATCHED_USER_QUERY, {"username": username})
        if response:
            return response['data']['matchedUser']['profile']
    except Exception as e:
        print(f"Error fetching user profile for {username}: {e}")
    return None

def fetch_submitted_questions(username, limit=500):
    try:
        return send_query(QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})['data']['recentAcSubmissionList']
    except Exception as e:
        print(f"Error fetching submitted questions for {username}: {e}")
    return []

def fetch_language_problem_count(username):
    try:
        return send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})['data']['matchedUser']['languageProblemCount']
    except Exception as e:
        print(f"Error fetching language problem count for {username}: {e}")
    return []

def fetch_all_questions():
    try:
        query_vars = {"categorySlug": "all-code-essentials", "skip": 0, "limit": 5000, "filters": {}}
        return send_query(ALL_QUESTION_LIST_QUERY, query_vars)['data']['problemsetQuestionList']['questions']
    except Exception as e:
        print(f"Error fetching all questions: {e}")
    return []

def get_user_instance(id):
    try:
        return Leetcode.objects.get(pk=id)
    except Exception as e:
        print(f"Error getting user instance for id {id}: {e}")
    return None

def update_user_instance(instance: Leetcode, user_data, matched_questions, latest_solved, total_solved, language_problem_count):
    try:
        if instance and user_data:
            instance.name = user_data.get('realName', '')
            instance.leetcode_rank = user_data.get('ranking', '')
            instance.photo_url = user_data.get('userAvatar', '')
            instance.total_solved = sum(question['problemsSolved'] for question in language_problem_count)
            instance.matched_ques = len(list(matched_questions.keys()))
            instance.submission_dict = latest_solved
            instance.matched_ques_dict = matched_questions
            instance.total_solved_dict = total_solved
            instance.save()
    except Exception as e:
        print(f"Error updating user instance: {e}")

def process_submissions(submitted_questions, all_question_list):
    try:
        titleSlug_to_id = {question['titleSlug']: question['frontendQuestionId'] for question in all_question_list}
        return [
            [titleSlug_to_id[question['titleSlug']], question['titleSlug'], question['timestamp']]
            for question in submitted_questions if question['titleSlug'] in titleSlug_to_id
        ] # [leetcode_id, titleSlug, timestamp]
    except Exception as e:
        print(f"Error processing submissions: {e}")
    return []

def generate_leaderboards_entries():
    try:
        questions = Question.objects.all()
        ques_given = [
            [question.leetcode_id, question.titleSlug, time.mktime(question.questionDate.timetuple())]
            for question in questions
        ]
        user_instances = Leetcode.objects.all()
        for user_instance in user_instances:
            username = user_instance.username
            solved_dict = user_instance.total_solved_dict
            solved_within_one_day, solved_within_one_week, solved_within_one_month = cal_solved_intervals(ques_given, solved_dict)
            print(f"user: {username} - Solved_dict: {solved_dict}")
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
    except Exception as e:
        print(f"Error generating leaderboard entries: {e}")

def update_rank(user_list, rank_dict, rank_type):
    try:
        for idx, user in enumerate(user_list):
            user_obj = Leetcode.objects.get(username=user[0])
            '''This code is commented out because it is not necessary to skip users with 0 questions solved.'''
            # if user[1] == 0:
            #     continue
            rank_dict[idx+1] =  {
                "username": user[0],
                "photo_url": user_obj.photo_url,
                "ques_solv": user[1],
                "last_solv": user[2]
            }

            try:
                user_obj = Leetcode.objects.get(username=user[0])
                if hasattr(user_obj, rank_type):  # Check if the attribute exists
                    setattr(user_obj, rank_type, idx+1)
                    user_obj.save()
                else:
                    print(f"Attribute {rank_type} does not exist on leetcode_acc objects.")
            except Leetcode.DoesNotExist:
                print(f"User {user[0]} does not exist.")
    except Exception as e:
        print(f"Error updating rank: {e}")

@shared_task(bind=True)
def calculate_leaderboards(self, *args, **kwargs):
    try:
        generate_leaderboards_entries()
        one_day, one_week, one_month = {}, {}, {}
        daily, weekly, monthly = [], [], []

        users = Leetcode.objects.all()
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

        update_rank(daily, one_day, 'daily_rank')
        update_rank(weekly, one_week, 'weekly_rank')
        update_rank(monthly, one_month, 'monthly_rank')
        
        # create or update leaderboard (total 3)
        Leaderboard.objects.update_or_create(
            leaderboard_type='daily', defaults={'leaderboard_data': one_day}
        )
        Leaderboard.objects.update_or_create(
            leaderboard_type='weekly', defaults={'leaderboard_data': one_week}
        )
        Leaderboard.objects.update_or_create(
            leaderboard_type='monthly', defaults={'leaderboard_data': one_month}
        )

        print("Leaderboards calculated successfully")
        return one_day, one_week, one_month
    except Exception as e:
        print(f"Error calculating leaderboards: {e}")
        return {}

@shared_task(bind=True)
def get_user_data(self, username, id, *args, **kwargs):
    try:
        user_profile = fetch_user_profile(username)
        if not user_profile:
            print(f"No profile data found for user {username}")
            return

        submitted_questions = fetch_submitted_questions(username)
        language_problem_count = fetch_language_problem_count(username)
        all_question_list = fetch_all_questions()

        submissions = process_submissions(submitted_questions, all_question_list)
        latest_solved = get_latest_submissions(submissions)

        user_instance = get_user_instance(id)
        if not user_instance:
            print(f"Failed to get or create user instance for user {username}")
            return

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
    except Exception as e:
        print(f"Error fetching or updating data for user {username}: {e}")

@shared_task(bind=True)
def refresh_user_data(self):
    try:
        users = Leetcode.objects.all()
        if not users:
            return

        user_data_tasks = [get_user_data.s(user.username, user.id) for user in users]
        task_chain = group(user_data_tasks) | calculate_leaderboards.s()
        task_chain.apply_async()
        print("Data refreshed and leaderboard initiated successfully")
    except Exception as e:
        print(f"Error refreshing user data: {e}")
