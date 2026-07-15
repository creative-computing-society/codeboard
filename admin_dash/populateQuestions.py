import logging
from django.utils import timezone
from leaderboard.models import Question
from leaderboard.utility import fetch_all_questions

# Define a logger for this module
logger = logging.getLogger(__name__)

def populate_question_model(frontendQuestionId):
    try:
        logger.info(f"Populating question model for frontendQuestionId {frontendQuestionId}...")
        
        questions_dict = fetch_all_questions()
        question_data = questions_dict.get(str(frontendQuestionId))
        
        if question_data:
            # Map LeetCode difficulty to the model choices
            leetcode_difficulty = question_data.get('difficulty', '')
            difficulty_mapping = {
                "Easy": "Basic",
                "Medium": "Intermediate",
                "Hard": "Advanced"
            }
            difficulty = difficulty_mapping.get(leetcode_difficulty, "Basic")
            
            # Fetch or create the Question model instance
            obj, created = Question.objects.update_or_create(
                leetcode_id=int(question_data['frontendQuestionId']),
                defaults={
                    'title': question_data['title'],
                    'titleSlug': question_data['titleSlug'],
                    'difficulty': difficulty,
                }
            )
            
            # Check if the object was created or updated
            if created:
                logger.info(f"Question with frontendQuestionId {frontendQuestionId} created successfully.")
                obj.questionDate = timezone.now()
                obj.save()
            else:
                logger.info(f"Question with frontendQuestionId {frontendQuestionId} updated successfully.")
        else:
            logger.warning(f"Question with frontendQuestionId {frontendQuestionId} not found.")
    
    except Exception as e:
        logger.error(f"Error populating question model for frontendQuestionId {frontendQuestionId}: {e}")
