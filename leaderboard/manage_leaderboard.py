from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import pytz
from django.core.paginator import Paginator
from django.db.models import F
from leaderboard.models import Leetcode, LeaderboardEntry, Leaderboard, Question
import logging

logger = logging.getLogger('celery')

TIMEZONE = pytz.timezone('Asia/Kolkata')

def safe_timestamp_to_datetime(timestamp):
    try:
        return timezone.datetime.fromtimestamp(int(timestamp), TIMEZONE)
    except (ValueError, TypeError):
        return None

def cal_solved_intervals(questions, solved_dict: dict):
    intervals = {
        'day': timedelta(days=1),
        'week': timedelta(weeks=1),
        'month': timedelta(days=30)
    }
    solved_within = {interval: {} for interval in intervals}

    for question in questions:
        ques_id, ques_titleslug, question_timestamp = question
        question_datetime = safe_timestamp_to_datetime(question_timestamp)
        if not question_datetime:
            continue

        if str(ques_titleslug) in solved_dict:
            ques_solved_timestamp = safe_timestamp_to_datetime(solved_dict[ques_titleslug])
            if not ques_solved_timestamp or ques_solved_timestamp < question_datetime:
                continue

            time_difference = ques_solved_timestamp - question_datetime

            for interval, duration in intervals.items():
                if time_difference <= duration:
                    solved_within[interval][ques_titleslug] = ques_solved_timestamp

    return [solved_within[interval] for interval in ['day', 'week', 'month']]

@transaction.atomic
def generate_leaderboards_entries():
    try:
        questions = list(Question.objects.values_list('leetcode_id', 'titleSlug', 'questionDate'))
        ques_given = [[q[0], q[1], q[2].timestamp()] for q in questions]
        
        user_instances = Leetcode.objects.all()
        for user_instance in user_instances:
            solved_dict = user_instance.total_solved_dict
            solved_intervals = cal_solved_intervals(ques_given, solved_dict)
            
            for interval, solved in zip(['day', 'week', 'month'], solved_intervals):
                entry, _ = LeaderboardEntry.objects.update_or_create(
                    user=user_instance,
                    interval=interval,
                    defaults={
                        'questions_solved': len(solved),
                        'earliest_solved_timestamp': max(solved.values(), default=timezone.now()).timestamp()
                    }
                )
        
        logger.info("Leaderboard entries generated successfully")
    except Exception as e:
        logger.error(f"Error generating leaderboard entries: {e}")
        raise

def update_rank(user_list, rank_dict, interval):
    try:
        for idx, user in enumerate(user_list, start=1):
            try:
                user_obj = Leetcode.objects.get(username=user[0])
                rank_dict[idx] = {
                    "username": user[0],
                    "photo_url": user_obj.photo_url,
                    "ques_solv": user[1],
                    "last_solv": user[2],
                    "rank": idx
                }
                
                # Update rank in Leetcode model
                if interval == 'day':
                    user_obj.daily_rank = idx
                elif interval == 'week':
                    user_obj.weekly_rank = idx
                elif interval == 'month':
                    user_obj.monthly_rank = idx
                # user_obj.save(update_fields=[f'{interval}ly_rank'])
                user_obj.save()
                
            except Leetcode.DoesNotExist:
                logger.warning(f"User {user[0]} does not exist.")
    except Exception as e:
        logger.error(f"Error updating rank: {e}")

@shared_task(bind=True)
def calculate_leaderboards(self, *args, **kwargs):
    try:
        generate_leaderboards_entries()
        leaderboards = {'daily': {}, 'weekly': {}, 'monthly': {}}
        
        for interval in ['day', 'week', 'month']:
            entries = LeaderboardEntry.objects.filter(interval=interval).select_related('user').order_by(
                F('questions_solved').desc(),
                F('earliest_solved_timestamp').asc()
            )
            
            user_list = [
                [entry.user.username, entry.questions_solved, 
                 timezone.datetime.fromtimestamp(entry.earliest_solved_timestamp, TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')]
                for entry in entries
            ]
            
            leaderboard_key = f"{interval}ly" if interval != 'day' else 'daily'
            update_rank(user_list, leaderboards[leaderboard_key], interval)
        
        for leaderboard_type, data in leaderboards.items():
            Leaderboard.objects.update_or_create(
                leaderboard_type=leaderboard_type,
                defaults={'leaderboard_data': data}
            )
        
        logger.info("Leaderboards calculated successfully")
        return leaderboards
    except Exception as e:
        logger.error(f"Error calculating leaderboards: {e}")
        return {}

def get_paginated_leaderboard(leaderboard_type, page=1, per_page=20):
    try:
        leaderboard = Leaderboard.objects.get(leaderboard_type=leaderboard_type)
        data = list(leaderboard.leaderboard_data.items())
        paginator = Paginator(data, per_page)
        return paginator.page(page)
    except Exception as e:
        logger.error(f"Error retrieving paginated leaderboard: {e}")
        return []