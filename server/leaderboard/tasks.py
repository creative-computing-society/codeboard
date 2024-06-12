from celery import shared_task
from .models import *
from .query_manager import *

def match_questions(questions_given, questions_solved):
    return [question for question in questions_given if question in questions_solved]

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
    #array of all questions, each question has frontendQuestionId and titleSlug
    all_question_list = send_query(ALL_QUESTION_LIST_QUERY,all_question_list_var)['data']['problemsetQuestionList']['questions']
    #make a map of titleSlug to frontendQuestionId
    titleSlug_to_id = {question['titleSlug']: question['frontendQuestionId'] for question in all_question_list}


    # Extract solved question titleSlugs
    ques_solved_titles = [question['titleSlug'] for question in submitted_questions]
    ques_solved_timestamp = [question['timestamp'] for question in submitted_questions]
    ques_solved_dict = {title: timestamp for title, timestamp in zip(ques_solved_titles, ques_solved_timestamp)}

    # Calculate total number of questions solved
    total_solved = sum(question['problemsSolved'] for question in language_problem_count)

    ques_solved_id = [titleSlug_to_id[title] for title in ques_solved_titles if title in titleSlug_to_id]

    # Fetch given question IDs
    questions_given_id = list(Question.objects.values_list('leetcode_id', flat=True))

    # Match questions
    matched_ques = match_questions(questions_given_id, ques_solved_id)
    
    # Update user data in the database
    instance = leetcode_acc.objects.get(user=user_id)
    instance.name = user_data['realName']
    instance.leetcode_rank = user_data['ranking']
    instance.photo_url = user_data['userAvatar']
    instance.total_solved = total_solved
    instance.matched_ques = len(matched_ques)
    instance.total_solved_list = ques_solved_id
    instance.matched_ques_list = matched_ques
    instance.save()

    print(f"Data for {username} saved successfully")

@shared_task(bind=True)
def refresh_user_data(self):
    users = leetcode_acc.objects.all()
    if not users:
        return

    for user in users:
        get_user_data.delay(user.leetcode_name, user.user)

    print("Data refreshed successfully")

@shared_task(bind=True)
def get_ques_id(self, titleSlug):
    response = send_query(QUESTION_ID_QUERY, {"titleSlug": titleSlug})
    return response['data']['question']['questionId']
