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
    titleSlug
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

QUESTION_ID_QUERY = '''
    query questionTitle($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
      }
    }
'''

def send_query(query, variables):
  url = "https://leetcode.com/graphql"
  headers = {"Content-Type": "application/json"}
  response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
  data = response.json()
  return data