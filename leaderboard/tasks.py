from celery import shared_task, group, chord
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.conf import settings
from .models import Leetcode
from .utility import (
    fetch_user_profile,
    fetch_recent_submissions,
    get_user_instance,
    get_all_ques_dict_from_db,
    verify_ques_submission
)
from .manage_leaderboard import calculate_leaderboards
import logging

logger = logging.getLogger('celery')
WORKER_COUNT = settings.CELERY_WORKER_CONCURRENCY
@transaction.atomic
def update_total_solved(recent_submissions, user_instance):
    total_solved_dict_in_db = user_instance.total_solved_dict
    for submission in recent_submissions:
        question_slug = submission['titleSlug']
        timestamp = submission['timestamp']
        if question_slug not in total_solved_dict_in_db or timestamp > total_solved_dict_in_db[question_slug]:
            total_solved_dict_in_db[question_slug] = timestamp
    user_instance.total_solved_dict = total_solved_dict_in_db
    user_instance.total_solved = len(total_solved_dict_in_db)
    user_instance.save()

@shared_task(bind=True, rate_limit='10/m', retry_backoff=True, max_retries=3)
def get_and_update_user_data(self, username, id, *args, **kwargs):
    try:
        userprofile = fetch_user_profile(username)
        if not userprofile:
            raise ValueError(f"No profile found for user {username}")

        recent_submissions = fetch_recent_submissions(username)
        if recent_submissions is None:
            raise ValueError(f"Failed to fetch recent submissions for user {username}")

        user_instance = get_user_instance(id)
        if not user_instance:
            raise Leetcode.DoesNotExist(f"User with id {id} not found")

        # Update user data
        user_instance.name = userprofile.get('realName', '')
        user_instance.photo_url = userprofile.get('userAvatar', '')
        user_instance.leetcode_rank = userprofile.get('ranking', 0)
        user_instance.submission_dict = recent_submissions

        # Validate data before saving
        try:
            user_instance.full_clean()
        except ValidationError as e:
            logger.error(f"Validation error for user {username}: {e}")
            return

        user_instance.save()

        # Update total solved questions
        update_total_solved(recent_submissions, user_instance)

        # Get given questions from db
        questions = get_all_ques_dict_from_db()
        n_matched_ques, matched_ques_dict = verify_ques_submission(questions, recent_submissions)
        user_instance.matched_ques = n_matched_ques
        user_instance.matched_ques_dict = matched_ques_dict
        user_instance.save()

        logger.info(f"Successfully updated data for user {username}")

    except Exception as e:
        logger.error(f"Error in get_and_update_user_data for user {username}: {e}")
        raise self.retry(exc=e)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def refresh_user_data(self):
    try:
        users = Leetcode.objects.all().order_by('id')
        total_users = users.count()
        
        if total_users == 0:
            logger.info("No users found to refresh")
            return

        # Determine the number of workers (this could be dynamic, based on the server configuration)
    
        page_size = max(1, total_users // WORKER_COUNT)  # Calculate page size to balance the load
        
        paginator = Paginator(users, page_size)
        
        # Process each page concurrently
        def process_page(page_number):
            page = paginator.page(page_number)
            user_data_tasks = [get_and_update_user_data.s(user.username, user.id) for user in page]
            return group(user_data_tasks)
        
        # Create a chord with a group of tasks for each page
        task_chain = chord(
            (process_page(page) for page in paginator.page_range),
            calculate_leaderboards.s()
        )
        task_chain.apply_async()

        logger.info(f"Data refresh initiated for {total_users} users across {WORKER_COUNT} workers, with {page_size} users per page.")
    except Exception as e:
        logger.error(f"Error refreshing user data: {e}")
        raise self.retry(exc=e) 

# Note: Ensure that the calculate_leaderboards task is properly defined in manage_leaderboard.py