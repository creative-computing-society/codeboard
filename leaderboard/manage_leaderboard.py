from celery import shared_task
from leaderboard.models import Leetcode, LeaderboardEntry, Leaderboard, Question
from django.utils import timezone
from datetime import timedelta
import time

def cal_solved_intervals(questions, solved_dict: dict):
    current_time = timezone.now()
    one_day_interval = current_time - timedelta(days=1)
    one_week_interval = current_time - timedelta(weeks=1)
    one_month_interval = current_time - timedelta(days=30)  # Approximation for a month

    solved_within_one_day = {}
    solved_within_one_week = {}
    solved_within_one_month = {}

    for question in questions:
        ques_titleslug = question[1]
        question_timestamp = int(question[2])
        if str(ques_titleslug) in solved_dict:
            ques_solved_timestamp = int(solved_dict[ques_titleslug])
            if ques_solved_timestamp < question_timestamp:
                # print(f"Question: {question_id} - Solved before creation")
                continue  # Skip if question was solved before it was created

            if ques_solved_timestamp >= one_day_interval.timestamp():
                solved_within_one_day[ques_titleslug] = ques_solved_timestamp
                # print(f"Question: {question_id} - Solved within one day")
            
            if ques_solved_timestamp >= one_week_interval.timestamp():
                solved_within_one_week[ques_titleslug] = ques_solved_timestamp
                # print(f"Question: {question_id} - Solved within one week")

            if ques_solved_timestamp >= one_month_interval.timestamp():
                solved_within_one_month[ques_titleslug] = ques_solved_timestamp
                # print(f"Question: {question_id} - Solved within one month")
        else:
            # print(f"Question: {question_id} - Not solved")
            pass

    return solved_within_one_day, solved_within_one_week, solved_within_one_month


def generate_leaderboards_entries():
    try:
        questions = Question.objects.all()
        ques_given = [
            [question.leetcode_id, question.titleSlug, question.questionDate.timestamp()]
            for question in questions
        ]
        user_instances = Leetcode.objects.all()
        for user_instance in user_instances:
            username = user_instance.username
            solved_dict = user_instance.total_solved_dict
            solved_within_one_day, solved_within_one_week, solved_within_one_month = cal_solved_intervals(ques_given, solved_dict)
            # print(f"user: {username} - Solved_dict: {solved_dict}")
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

        # print("Leaderboards calculated successfully")
        return one_day, one_week, one_month
    except Exception as e:
        print(f"Error calculating leaderboards: {e}")
        return {}