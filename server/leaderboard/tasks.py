from celery import shared_task
from .models import *
from .query_manager import *

def match_questions(questions_given, questions_solved):
    matched_ques = []
    for question in questions_given:
        if question in questions_solved:
            matched_ques.append(question)
    return matched_ques

@shared_task(bind=True)
def get_user_data(self, username, user_id):
    limit = 500

    response = send_query(MATCHED_USER_QUERY, {"username": username})
    response2 = send_query(QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})
    response3 = send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})

    data = response
    data2 = response2
    data3 = response3

    data2 = data2['data']['recentAcSubmissionList']
    data3 = data3['data']['matchedUser']['languageProblemCount']

    questions_solved = []
    for question in data2:
        questions_solved.append(question['titleSlug'])

    number_of_questions = 0
    for question in data3:
        number_of_questions += question['problemsSolved']

    questions_solved_id = []
    for question in questions_solved:
        response = send_query(QUESTION_ID_QUERY, {"titleSlug": question})
        question_id = response['data']['question']['questionId']
        # convert the question id to integer
        question_id = int(question_id)
        questions_solved_id.append(question_id)

    profile = data['data']['matchedUser']['profile']
    realname = profile['realName']
    rank = profile['ranking']
    photo_url = profile['userAvatar']

    questions_given_id = fetch_given_ques()

    matched_ques = match_questions(questions_given_id, questions_solved_id)
    instance = leetcode_acc.objects.get(user=user_id)

    # save the details in the model
    instance.name = realname
    instance.leetcode_rank = rank
    instance.photo_url = photo_url
    instance.total_solved = number_of_questions
    instance.matched_ques = len(matched_ques)
    instance.total_solved_list = questions_solved_id
    instance.matched_ques_list = matched_ques
    instance.save()
    
    print(f"Data for {username} saved successfully")

def fetch_given_ques():
    questions_given = Question.objects.all()
    questions_given_id = []
    for question in questions_given:
        questions_given_id.append(question.leetcode_id)
    return questions_given_id


@shared_task(bind=True)
def refresh_user_data(self):
    users = leetcode_acc.objects.all()
    if users is None:
        return
    for user in users:
        get_user_data.delay(user.leetcode_name, user.user)
    print("Data refreshed successfully")

@shared_task(bind=True)
def get_ques_id(self, titleSlug):
    response = send_query(QUESTION_ID_QUERY, {"titleSlug": titleSlug})
    question_id = response['data']['question']['questionId']
    return question_id