from celery import shared_task
from .models import *
from .query_manager import *

def fetch_admin_questions():
    ques = Question.objects.all()
    return [q.leetcode_id for q in ques]

def match_ques(questions_solved_ids):
    admin_questions_ids = fetch_admin_questions()
    return [ques for ques in questions_solved_ids if ques in admin_questions_ids]

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
        questions_solved_id.append(question_id)

    profile = data['data']['matchedUser']['profile']
    realname = profile['realName']
    rank = profile['ranking']
    photo_url = profile['userAvatar']

    instance = leetcode_acc.objects.get(user=user_id)

    matched_ques = match_ques(questions_solved_id)
    print('Matched Questions' +matched_ques)
    # save the details in the model
    instance.name = realname
    instance.rank = rank
    instance.photo_url = photo_url
    instance.number_of_questions = number_of_questions
    instance.SolvedQuestions = questions_solved_id
    # instance.MatchedQuestions = matched_ques
    instance.save()
    
    print(f"Data for {username} saved successfully")


@shared_task(bind=True)
def refresh_user_data(self):
    users = leetcode_acc.objects.all()
    if users is None:
        return
    for user in users:
        get_user_data.delay(user.leetcode_name, user.user)

def match_ques(ques_solved_ids):
    pass

@shared_task(bind=True)
def get_ques_id(self, titleSlug):
    response = send_query(QUESTION_ID_QUERY, {"titleSlug": titleSlug})
    question_id = response['data']['question']['questionId']
    return question_id