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
    timestamp
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

ALL_QUESTION_LIST_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    questions: data {
      frontendQuestionId: questionFrontendId
      titleSlug
    }
  }
}
"""

def send_query(query, variables):
  url = "https://leetcode.com/graphql"
  headers = {"Content-Type": "application/json"}
  response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
  data = response.json()
  return data