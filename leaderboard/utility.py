from django.core.cache import cache
from leaderboard.models import *
from .query_manager import *
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Adjust as needed

def fetch_user_profile(username):
    '''Fetch user profile from Leetcode'''
    try:
        response = send_query(MATCHED_USER_QUERY, {"username": username})
        if response:
            logger.info(f"Fetched profile for user {username}")
            return response['data']['matchedUser']['profile']
    except Exception as e:
        logger.error(f"Error fetching user profile for {username}: {e}")
    return None

def fetch_recent_submissions(username, limit=50):
    '''Fetch recent submissions from Leetcode'''
    try:
        response = send_query(RECENT_QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})
        if response:
            logger.info(f"Fetched recent submissions for user {username}")
            return response['data']['recentAcSubmissionList']
    except Exception as e:
        logger.error(f"Error fetching recent submissions for {username}: {e}")
    return None

CACHE_TIMEOUT = 60 * 60
def fetch_all_questions():
    '''Fetch all questions from Leetcode'''
    cache_key = 'all_questions_dict'
    questions_dict = cache.get(cache_key)

    if not questions_dict:
        try:
            query_vars = {"categorySlug": "all-code-essentials", "skip": 0, "limit": 5000, "filters": {}}
            questions_list = send_query(ALL_QUESTION_LIST_QUERY, query_vars)['data']['problemsetQuestionList']['questions']
            questions_dict = {question['frontendQuestionId']: question for question in questions_list}
            cache.set(cache_key, questions_dict, timeout=CACHE_TIMEOUT)
            logger.info(f"Fetched and cached {len(questions_dict)} questions.")
            return questions_dict
        except Exception as e:
            logger.error(f"Error fetching all questions: {e}")
            return {}
    else:
        logger.info(f"Fetched {len(questions_dict)} questions from cache.")
        return questions_dict

def get_user_instance(id):
    '''Get user instance from DB'''
    try:
        user_instance = Leetcode.objects.get(id=id)
        logger.info(f"Fetched user instance with ID {id}")
        return user_instance
    except Leetcode.DoesNotExist:
        logger.warning(f"User with id {id} does not exist")
    return None

def get_all_ques_dict_from_db():
    '''Get all questions from DB'''
    questions = Question.objects.all()
    questions_dict = [
        {
            "titleSlug": question.titleSlug,
            "timestamp": question.questionDate.timestamp()
        }
        for question in questions
    ]
    logger.info(f"Fetched {len(questions_dict)} questions from the database")
    return questions_dict

def verify_ques_submission(ques_given, recent_submissions):
    '''Verify recent submissions against given questions'''
    matched_ques_dict = {}
    ques_dict = {q["titleSlug"]: q["timestamp"] for q in ques_given}

    for submission in recent_submissions:
        title_slug = submission["titleSlug"]
        submission_time = submission["timestamp"]

        if title_slug in ques_dict and float(submission_time) > float(ques_dict[title_slug]):
            matched_ques_dict[title_slug] = submission_time

    logger.info(f"Matched {len(matched_ques_dict)} questions out of {len(ques_given)} given questions")
    return len(matched_ques_dict), matched_ques_dict
