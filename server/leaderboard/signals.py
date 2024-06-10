from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from .models import leetcode_acc

def send_query(username, query):
    url = "https://leetcode.com/graphql"

    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()
    return data

@receiver(post_save, sender=leetcode_acc)
def get_user_data(sender, instance, created, **kwargs):
    username = instance.leetcode_name
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
    response = send_query(username, query)
    response3 = send_query(username, query3)

    data = response
    data3 = response3
    profile = data['data']['matchedUser']['profile']
    realname = profile['realName']
    rank = profile['ranking']
    photo_url = profile['userAvatar']
    last_solved = "Not available"
    number_of_questions = 0
    questions = data3['data']['matchedUser']['languageProblemCount']
    for question in questions:
        number_of_questions += question['problemsSolved']

    # save the details the model
    instance.name = realname
    instance.rank = rank
    instance.photo_url = photo_url
    instance.number_of_questions = number_of_questions
    instance.last_solved = last_solved
    instance.save()
    
    print(f"Data for {username} saved successfully")

