import logging
import requests
from .models import Leetcode

logger = logging.getLogger(__name__)

MATCHED_USER_QUERY = '''
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

RECENT_QUESTIONS_SUBMITTED_QUERY = '''
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
      title
      difficulty
    }
  }
}
"""

def send_query(query, variables):
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Request timed out.")
        return {"error": "Request timed out."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return {"error": f"Request error: {str(e)}"}

    try:
        data = response.json()
        if "errors" in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            return {"error": "GraphQL errors occurred.", "details": data["errors"]}
        return data
    except requests.exceptions.JSONDecodeError:
        logger.error("Failed to decode JSON response.")
        return {"error": "Failed to decode JSON response.", "status_code": response.status_code, "text": response.text}
