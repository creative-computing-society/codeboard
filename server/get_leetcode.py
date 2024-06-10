from django.db.models.signals import post_save
from django.dispatch import receiver
import requests, json

def send_query(query):
    url = "https://leetcode.com/graphql"

    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()
    return data

def get_user_data():
    username = "hushraj"
    limit = 500
    query = f"""
    {{
      matchedUser(username:"{username}") {{
        profile {{
            ranking
            realName
            userAvatar
            solutionCount
        }}
      }}
    }}
    """
    query2 = f"""
    {{
        recentAcSubmission(username:"{username}", limit:"{limit}") {{
            id
            title
            titleSlug
            timestamp
        }}
    }}
    """
    query3 = f"""
    {{
      matchedUser(username:"{username}") {{
        languageProblemCount {{
            problemsSolved
        }}
      }}
    }}
    """
    response = send_query(query)
    response3 = send_query(query3)

    data = response
    data3 = response3

    print(data)
    print(data3)

    profile = data['data']['matchedUser']['profile']
    realname = profile['realName']
    rank = profile['ranking']
    photo_url = profile['userAvatar']
    questions_arr = data3['data']['matchedUser']['languageProblemCount']
    number_of_questions = 0
    for question in questions_arr:
        number_of_questions += question['problemsSolved']
    last_solved = "Not available"
    
    print(f"Real name: {realname}")
    print(f"Rank: {rank}")
    print(f"Photo URL: {photo_url}")
    print(f"Number of questions: {number_of_questions}")
    print(f"Last solved: {last_solved}")

    print(f"Data for {username} saved successfully")


get_user_data()