import asyncio
from logging import getLogger

from asgiref.sync import sync_to_async
from celery import shared_task, Task, chord

from django.utils import timezone

from .models import Leetcode, LeaderboardEntry, Question, Leaderboard
from .utils import (
    generate_leaderboard_entries,
    match_questions_to_solved,
    update_user_instance,
    update_rank,
    process_submissions,
    get_latest_submissions,
)
from .utils import run_coro

from .query_manager import (
    fetch_user_profile,
    fetch_all_questions,
    fetch_language_problem_count,
    fetch_submitted_questions,
)

logger = getLogger(__name__)


@shared_task
def calculate_leaderboards():
    return run_coro(_calculate_leaderboards())


@shared_task
def get_user_data(username: str, id: int, *args, **kwargs):
    return run_coro(_get_user_data(username, id, args, kwargs))


async def _calculate_leaderboards():
    try:
        one_day, one_week, one_month = {}, {}, {}
        daily, weekly, monthly, coros = [], [], [], []

        users, _ = await asyncio.gather(
            sync_to_async(list)(Leetcode.objects.all()), generate_leaderboard_entries()
        )

        for user in users:
            for interval in ["day", "week", "month"]:
                coros.append(
                    LeaderboardEntry.objects.aget(user=user, interval=interval)
                )

        entries = await asyncio.gather(*coros)

        for i, user in enumerate(users):
            daily_entry = entries[i * 3]
            weekly_entry = entries[i * 3 + 1]
            monthly_entry = entries[i * 3 + 2]

            daily.append(
                [
                    user.username,
                    daily_entry.questions_solved,
                    daily_entry.earliest_solved_timestamp,
                ]
            )
            weekly.append(
                [
                    user.username,
                    weekly_entry.questions_solved,
                    weekly_entry.earliest_solved_timestamp,
                ]
            )
            monthly.append(
                [
                    user.username,
                    monthly_entry.questions_solved,
                    monthly_entry.earliest_solved_timestamp,
                ]
            )

        daily.sort(key=lambda x: (-x[1], x[2]))
        weekly.sort(key=lambda x: (-x[1], x[2]))
        monthly.sort(key=lambda x: (-x[1], x[2]))

        # convert timestamp to human readable format
        for user in daily:
            user[2] = timezone.datetime.fromtimestamp(user[2]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        for user in weekly:
            user[2] = timezone.datetime.fromtimestamp(user[2]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        for user in monthly:
            user[2] = timezone.datetime.fromtimestamp(user[2]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # create or update leaderboard (total 3)
        await asyncio.gather(
            update_rank(daily, one_day, "daily_rank"),
            update_rank(weekly, one_week, "weekly_rank"),
            update_rank(monthly, one_month, "monthly_rank"),
            Leaderboard.objects.aupdate_or_create(
                leaderboard_type="daily", defaults={"leaderboard_data": one_day}
            ),
            Leaderboard.objects.aupdate_or_create(
                leaderboard_type="weekly", defaults={"leaderboard_data": one_week}
            ),
            Leaderboard.objects.aupdate_or_create(
                leaderboard_type="monthly", defaults={"leaderboard_data": one_month}
            ),
        )

        logger.info("Leaderboards calculated successfully")
        return one_day, one_week, one_month
    except Exception as e:
        logger.error(f"Error calculating leaderboards: {e}")
        return {}


async def _get_user_data(username, id, *args, **kwargs):
    try:
        user_profile = await fetch_user_profile(username)
        if not user_profile:
            logger.info(f"No profile data found for user {username}")
            return

        (
            submitted_questions,
            language_problem_count,
            all_question_list,
            user_instance,
        ) = await asyncio.gather(
            fetch_submitted_questions(username),
            fetch_language_problem_count(username),
            fetch_all_questions(),
            Leetcode.objects.aget(pk=id),
        )
        submissions = await asyncio.to_thread(
            process_submissions, submitted_questions, all_question_list
        )
        latest_solved = await asyncio.to_thread(get_latest_submissions, submissions)

        if not user_instance:
            logger.warning(f"Failed to get or create user instance for user {username}")
            return

        total_solved = user_instance.total_solved_dict

        total_solved.update(
            {k: v for k, v in latest_solved.items() if k not in total_solved}
        )

        async def fetch_questions():
            return [
                [leetcode_id, title_slug, question_date.timestamp()]
                async for leetcode_id, title_slug, question_date in Question.objects.values_list(
                    "leetcode_id", "titleSlug", "questionDate"
                )
            ]

        # Fetch only the needed fields
        ques_given = await fetch_questions()

        matched_ques = await asyncio.to_thread(
            match_questions_to_solved, ques_given, total_solved
        )

        await update_user_instance(
            user_instance,
            user_profile,
            matched_ques,
            latest_solved,
            total_solved,
            language_problem_count,
        )

    except Exception as e:
        logger.error(f"Error fetching or updating data for user {username}: {e}")


# User's data was not updating cause it's schedular is not set in Django's admin panel thorugh django-celery-beats
# Eather we can set it staticly in celery.py or dynamically in Django's admin panel
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def refresh_user_data(self: Task):
    try:
        users = Leetcode.objects.values("id", "username")
        if not users:
            return

        user_data_tasks = [get_user_data.s(u["username"], u["id"]) for u in users]  # type:ignore

        # Run all user updates, then trigger leaderboard
        chord(user_data_tasks)(calculate_leaderboards.s())  # type: ignore

        logger.info("Data refreshed and leaderboard initiated successfully")
    except Exception as e:
        raise self.retry(countdown=30, exec=e)
