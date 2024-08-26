from django.core.cache import cache
from leaderboard.models import *
from .query_manager import *
import json

def fetch_user_profile(username):
    '''fetch user profile from leetcode
    {
    "ranking": 1234,
    "userAvatar": "https://example.com/avatar.jpg",
    "realName": "John Doe"
    }
    '''
    try:
        response = send_query(MATCHED_USER_QUERY, {"username": username})
        if response:
            # print(json.dumps(response, indent=2))
            return response['data']['matchedUser']['profile']
    except Exception as e:
        print(f"Error fetching user profile for {username}: {e}")
    return None

def fetch_recent_submissions(username, limit=50):
    '''fetch recent submissions from leetcode
    [
    {
    "titleSlug": "two-sum",
    "timestamp": 1724607327
    },
    {
    "titleSlug": "reverse-integer",
    "timestamp": 1718650907
    }
    ]
    '''
    try:
        response = send_query(RECENT_QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})
        if response:
            # print(json.dumps(response, indent=2))
            return response['data']['recentAcSubmissionList']
    except Exception as e:
        print(f"Error fetching recent submissions for {username}: {e}")
    return None

CACHE_TIMEOUT = 60 * 60
def fetch_all_questions():
    '''fetch all questions from leetcode
    [
    {
    "frontendQuestionId": "1",
    "titleSlug": "two-sum",
    "title": "Two Sum",
    "difficulty": "Easy"
    },
    {
    "frontendQuestionId": "2",
    "titleSlug": "add-two-numbers",
    "title": "Add Two Numbers",
    "difficulty": "Medium"
    }
    ]
    '''
    cache_key = 'all_questions_dict'
    questions_dict = cache.get(cache_key)

    if not questions_dict:
        try:
            query_vars = {"categorySlug": "all-code-essentials", "skip": 0, "limit": 5000, "filters": {}}
            questions_list = send_query(ALL_QUESTION_LIST_QUERY, query_vars)['data']['problemsetQuestionList']['questions']
            questions_dict = {question['frontendQuestionId']: question for question in questions_list}
            cache.set(cache_key, questions_dict, timeout=CACHE_TIMEOUT)
            print(f"Fetched and cached {len(questions_dict)} questions.")
            return questions_dict
        except Exception as e:
            print(f"Error fetching all questions: {e}")
            return {}
    else:
        print(f"Fetched {len(questions_dict)} questions from cache.")
        return questions_dict

def get_user_instance(id):
    '''get user instance from db'''
    try:
        user_instance = Leetcode.objects.get(id=id)
        return user_instance
    except Leetcode.DoesNotExist:
        print(f"User with id {id} does not exist")
    return None

def get_all_ques_dict_from_db():
    '''get all questions from db
    [
    {
    "titleSlug": "two-sum",
    "timestamp": 1724607327
    },
    {
    "titleSlug": "reverse-integer",
    "timestamp": 1718650907
    }
    ]
    '''
    questions = Question.objects.all()
    questions = [
        {
            "titleSlug": question.titleSlug,
            "timestamp": question.questionDate.timestamp()
        }
        for question in questions
    ]
    return questions

def verify_ques_submission(ques_given, recent_submissions):
    '''**Example usage:**\n
    ques_given = [
        {"titleSlug": "two-sum", "timestamp": 1724600000},
        {"titleSlug": "reverse-integer", "timestamp": 1718650000}
    ]

    recent_submissions = [
        {"titleSlug": "two-sum", "timestamp": 1724607327},
        {"titleSlug": "reverse-integer", "timestamp": 1718650907}
    ]\n
    **Output:**\n {'two-sum': 1724607327, 'reverse-integer': 1718650907}
    '''
    matched_ques_dict = {}
    ques_dict = {q["titleSlug"]: q["timestamp"] for q in ques_given}

    for submission in recent_submissions:
        title_slug = submission["titleSlug"]
        submission_time = submission["timestamp"]

        if title_slug in ques_dict and float(submission_time) > float(ques_dict[title_slug]):
            matched_ques_dict[title_slug] = submission_time

    return len(matched_ques_dict), matched_ques_dict