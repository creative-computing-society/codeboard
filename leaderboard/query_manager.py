import asyncio
import aiohttp
from typing import Any, Dict, Optional, List
from logging import getLogger

from . import get_session

logger = getLogger(__name__)

MATCHED_USER_QUERY = """
  query userPublicProfile($username: String!) {
    matchedUser(username: $username) {
    profile {
      ranking
      userAvatar
      realName
    }
    }
  }
"""

QUESTIONS_SUBMITTED_QUERY = """
  query recentAcSubmissions($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
    titleSlug
    timestamp
    }
  }
"""

LANGUAGE_PROBLEM_COUNT_QUERY = """
  query languageStats($username: String!) {
    matchedUser(username: $username) {
    languageProblemCount {
      languageName
      problemsSolved
    }
    }
  }
"""

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

TIMEOUT = aiohttp.ClientTimeout(total=5)
URL = "https://leetcode.com/graphql"
HEADERS = {"Content-Type": "application/json"}


async def send_query(query, variables) -> Optional[Dict[str, Any]]:
    data = None
    json = {"query": query, "variables": variables}
    session = await get_session()

    try:
        async with session.post(
            URL, json=json, headers=HEADERS, timeout=TIMEOUT
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

    except aiohttp.ClientConnectionError as e:
        logger.error(f"Client could not connect! {e}")

    except asyncio.TimeoutError:
        logger.error("Query was timed out!")

    return data


async def fetch_user_profile(username):
    try:
        response = await send_query(MATCHED_USER_QUERY, {"username": username})
        if response:
            return response["data"]["matchedUser"]["profile"]
    except Exception as e:
        print(f"Error fetching user profile for {username}: {e}")


async def fetch_submitted_questions(username, limit=500) -> List[Dict[str, Any]]:
    try:
        query = await send_query(
            QUESTIONS_SUBMITTED_QUERY, {"username": username, "limit": limit}
        )
        assert query is not None
        return query["data"]["recentAcSubmissionList"]
    except Exception as e:
        print(f"Error fetching submitted questions for {username}: {e}")

    return []


async def fetch_language_problem_count(username):
    try:
        query = await send_query(LANGUAGE_PROBLEM_COUNT_QUERY, {"username": username})
        assert query is not None

        return query["data"]["matchedUser"]["languageProblemCount"]
    except Exception as e:
        print(f"Error fetching language problem count for {username}: {e}")
    return []


# TODO: Cache the result as questions only update every day only
async def fetch_all_questions() -> List[Dict[str, Any]]:
    try:
        query_vars = {
            "categorySlug": "all-code-essentials",
            "skip": 0,
            "limit": 5000,
            "filters": {},
        }

        query = await send_query(ALL_QUESTION_LIST_QUERY, query_vars)
        assert query is not None
        return query["data"]["problemsetQuestionList"]["questions"]
    except Exception as e:
        print(f"Error fetching all questions: {e}")

    return []
