from celery import shared_task, group

from leaderboard.manage_leaderboard import calculate_leaderboards
from .models import Leetcode
from .utility import fetch_user_profile, fetch_recent_submissions, get_user_instance, get_all_ques_dict_from_db, verify_ques_submission

def update_total_solved(recent_submissions, user_instance):
    total_solved_dict_in_db = user_instance.total_solved_dict
    for submission in recent_submissions:
        question_slug = submission['titleSlug']
        total_solved_dict_in_db[question_slug] = submission['timestamp']
    user_instance.total_solved_dict = total_solved_dict_in_db
    user_instance.total_solved = len(total_solved_dict_in_db)
    user_instance.save()

@shared_task(bind=True)
def get_and_update_user_data(self, username, id, *args, **kwargs):
    '''fetch user data from leetcode and update in db'''
    try:
        userprofile = fetch_user_profile(username)
        if not userprofile:
            return
        recent_submissions = fetch_recent_submissions(username)
        user_instance = get_user_instance(id)
        if not user_instance:
            return
        
        user_instance.name = userprofile['realName']
        user_instance.photo_url = userprofile['userAvatar']
        user_instance.leetcode_rank = userprofile['ranking']
        user_instance.submission_dict = recent_submissions
        user_instance.save()

        # update total solved questions
        update_total_solved(recent_submissions, user_instance)

        # get given questions from db
        questions = get_all_ques_dict_from_db()
        n_matched_ques, matched_ques_dict = verify_ques_submission(questions, recent_submissions)
        user_instance.matched_ques = n_matched_ques
        user_instance.matched_ques_dict = matched_ques_dict
        user_instance.save()
    except Exception as e:
        print(f"Error in get_and_update_user_data: {e}")

@shared_task(bind=True)
def refresh_user_data(self):
    try:
        users = Leetcode.objects.all()
        if not users:
            return

        user_data_tasks = [get_and_update_user_data.s(user.username, user.id) for user in users]
        task_chain = group(user_data_tasks) | calculate_leaderboards.s()
        task_chain.apply_async()
        print("Data refreshed and leaderboard initiated successfully")
    except Exception as e:
        print(f"Error refreshing user data: {e}")



