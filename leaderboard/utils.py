import asyncio
from datetime import timedelta
from typing import Any, Dict, List, Tuple, Coroutine
from logging import getLogger
from asgiref.sync import sync_to_async

from django.utils import timezone

from .models import LeaderboardEntry, Leetcode, Question

logger = getLogger(__name__)


# Since using asyncio.run() creates a new event loop and we have alot of users, just run them in this loop
def run_coro(coro: Coroutine):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create a new loop
        return asyncio.run(coro)
    else:
        # Already in event loop, schedule task and wait
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()


def get_latest_submissions(submissions) -> Dict[int, int]:
    return {
        int(sub[0]): int(sub[2]) for sub in sorted(submissions, key=lambda s: int(s[2]))
    }


def match_questions_to_solved(questions, solved_submissions: dict) -> Dict[int, int]:
    return {
        int(qid): solved_submissions[int(qid)]
        for qid, _, qts in questions
        if (int(qid) in solved_submissions and solved_submissions[int(qid)] > int(qts))
    }


async def get_user_instance(id: int):
    try:
        return await Leetcode.objects.aget(pk=id)
    except Leetcode.DoesNotExist as e:
        print(f"Error getting user instance for id {id}: {e}")
    return None


async def update_user_instance(
    instance: Leetcode,
    user_data: Dict[str, Any],
    matched_questions: Dict,
    latest_solved: Dict,
    total_solved: Dict,
    language_problem_count: list,
):
    total_solved_count = sum(
        q.get("problemsSolved", 0) for q in (language_problem_count or [])
    )

    updates = {
        "name": user_data.get("realName", instance.name),
        "leetcode_rank": user_data.get("ranking", instance.leetcode_rank),
        "photo_url": user_data.get("userAvatar", instance.photo_url),
        "total_solved": total_solved_count,
        "matched_ques": len(matched_questions or {}),
        "submission_dict": latest_solved or {},
        "matched_ques_dict": matched_questions or {},
        "total_solved_dict": total_solved or {},
    }

    # Filters those values that differ from the instance and only update those
    dirty = {f: v for f, v in updates.items() if getattr(instance, f) != v}
    if dirty:
        for field, value in dirty.items():
            setattr(instance, field, value)
        await instance.asave(update_fields=dirty.keys())


# Function that returns Question ID, name and time at which it was submiited at
def process_submissions(
    submitted_questions: List[Dict[str, str]], all_question_list: List[Dict[str, str]]
) -> List[Tuple[int, str, int]]:
    titleSlug_to_id: Dict[str, int] = {
        question["titleSlug"]: int(question["frontendQuestionId"])
        for question in all_question_list
    }

    result: List[Tuple[int, str, int]] = []

    for question in submitted_questions:
        try:
            slug = question["titleSlug"]
            if slug not in titleSlug_to_id:
                continue
            timestamp = int(question["timestamp"])
            result.append((titleSlug_to_id[slug], slug, timestamp))

        except KeyError as e:
            logger.error(f"Missing key {e} in question: {question}")

        except ValueError as e:
            logger.error(f"Invalid value in question: {question}, error: {e}")

    return result


async def update_rank(user_list, rank_dict, rank_type):
    user_coro, save_coro, user_objs = [], [], []
    rank_dict = {}

    for idx, user in enumerate(user_list, 1):
        user_coro.append(Leetcode.objects.aget(username=user[0]))
        rank_dict[idx] = {
            "username": user[0],
            "ques_solv": user[1],
            "last_solv": user[2],
        }

    try:
        user_objs: List[Leetcode] = await asyncio.gather(*user_coro)
    except Leetcode.DoesNotExist:
        logger.error("One of the users does not exist!")

    for idx, user_obj in enumerate(user_objs, 1):
        setattr(user_obj, rank_type, idx)
        save_coro.append(user_obj.asave(update_fields=[rank_type]))

    await asyncio.gather(*save_coro)


async def generate_leaderboard_entries():
    tasks = []

    async def get_question_data():
        return [
            (leetcode_id, titleSlug, questionDate.timestamp())
            async for (
                leetcode_id,
                titleSlug,
                questionDate,
            ) in Question.objects.values_list(
                "leetcode_id", "titleSlug", "questionDate"
            )
        ]

    ques_given, user_instances = await asyncio.gather(
        get_question_data(),
        sync_to_async(list)(Leetcode.objects.all()),
    )

    for user in user_instances:
        tasks.append(process_user_leaderboard(user, ques_given))

    await asyncio.gather(*tasks)


def cal_solved_intervals(questions, solved_dict: dict):
    current_time = timezone.now()
    one_day_interval = current_time - timedelta(days=1)
    one_week_interval = current_time - timedelta(weeks=1)
    one_month_interval = current_time - timedelta(days=30)  # Approximation for a month

    solved_within_one_day = {}
    solved_within_one_week = {}
    solved_within_one_month = {}

    for question in questions:
        question_id = int(question[0])
        question_timestamp = int(question[2])
        if str(question_id) in solved_dict:
            ques_solved_timestamp = solved_dict[str(question_id)]
            if ques_solved_timestamp < question_timestamp:
                continue  # Skip if question was solved before it was created

            if ques_solved_timestamp >= one_day_interval.timestamp():
                solved_within_one_day[question_id] = ques_solved_timestamp

            if ques_solved_timestamp >= one_week_interval.timestamp():
                solved_within_one_week[question_id] = ques_solved_timestamp

            if ques_solved_timestamp >= one_month_interval.timestamp():
                solved_within_one_month[question_id] = ques_solved_timestamp

    return solved_within_one_day, solved_within_one_week, solved_within_one_month


async def process_user_leaderboard(user_instance: Leetcode, ques_given):
    solved_dict = user_instance.total_solved_dict

    # TODO: Find a way to convert these into 1 DB call instead of 3
    daily_coro = LeaderboardEntry.objects.aget_or_create(
        user=user_instance, interval="day"
    )
    weekly_coro = LeaderboardEntry.objects.aget_or_create(
        user=user_instance, interval="week"
    )
    monthly_coro = LeaderboardEntry.objects.aget_or_create(
        user=user_instance, interval="month"
    )

    # 3AM Ureka idea
    (solved_day, solved_week, solved_month), entries = await asyncio.gather(
        asyncio.to_thread(cal_solved_intervals, ques_given, solved_dict),
        asyncio.gather(daily_coro, weekly_coro, monthly_coro),
    )

    # Unpack results
    daily_entry, weekly_entry, monthly_entry = (entry for entry, _ in entries)

    # Instead of manually doing max and len for each entry, just use a loop
    for entry, solved in (
        (daily_entry, solved_day),
        (weekly_entry, solved_week),
        (monthly_entry, solved_month),
    ):
        entry.questions_solved = len(solved)
        entry.earliest_solved_timestamp = max(solved.values(), default=0)

    await LeaderboardEntry.objects.abulk_update(
        [daily_entry, weekly_entry, monthly_entry],
        ["questions_solved", "earliest_solved_timestamp"],
    )
