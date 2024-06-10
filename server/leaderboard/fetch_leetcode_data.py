import requests
from .models import leetcode_acc

MATCHED_USER_QUERY =  '''
    query userPublicProfile($username: String!) {
      matchedUser(username: $username) {
        profile {
          ranking
          userAvatar
          realName
        }
      }
    }
'''

QUESTIONS_SUBMITTED_QUERY = '''
    query recentAcSubmissions($username: String!, $limit: Int!) {
      recentAcSubmissionList(username: $username, limit: $limit) {
        id
      }
    }
'''

LANGUAGE_PROBLEM_COUNT_QUERY = '''
    query languageStats($username: String!) {
      matchedUser(username: $username) {
        languageProblemCount {
          languageName
          problemsSolved
        }
      }
    }
'''

def send_query(query, variables):
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    data = response.json()
    return data

def get_user_data(username, user_id):
    limit = 500

    response = send_query(MATCHED_USER_QUERY, {"username": username})
    response2 = send_query(QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit})
    response3 = send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})

    data = response
    data2 = response2
    data3 = response3

    data2 = data2['data']['recentAcSubmissionList']

    questions_solved = []
    for question in data2:
        questions_solved.append(question['id'])

    profile = data['data']['matchedUser']['profile']
    realname = profile['realName']
    rank = profile['ranking']
    photo_url = profile['userAvatar']
    last_solved = "Not available"
    number_of_questions = 0
    data3 = data3['data']['matchedUser']['languageProblemCount']
    for question in data3:
        number_of_questions += question['problemsSolved']

    instance = leetcode_acc.objects.get(user=user_id)
    # save the details the model
    instance.name = realname
    instance.rank = rank
    instance.photo_url = photo_url
    instance.number_of_questions = number_of_questions
    instance.last_solved = last_solved
    instance.SolvedQuestions = questions_solved
    instance.save()
    
    print(f"Data for {username} saved successfully")

