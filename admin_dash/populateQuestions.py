from django.utils import timezone
from leaderboard.models import Question
from leaderboard.utility import fetch_all_questions

def populate_question_model(frontendQuestionId):
    try:
        print(f"Populating question model for frontendQuestionId {frontendQuestionId}...")
        
        # Fetch questions dictionary from cache or API
        questions_dict = fetch_all_questions()

        # Check if the question exists in the fetched data
        question_data = questions_dict.get(str(frontendQuestionId))
        
        if question_data:
            # Fetch or create the Question model instance
            obj, created = Question.objects.update_or_create(
                leetcode_id=int(question_data['frontendQuestionId']),
                defaults={
                    'title': question_data['title'],
                    'titleSlug': question_data['titleSlug'],
                    'difficulty': question_data['difficulty'],
                    'questionDate': timezone.now(),  # You might want to use the actual date of the question here
                }
            )
            
            # Check if the object was actually updated or created
            if created:
                print(f"Question with frontendQuestionId {frontendQuestionId} created successfully.")
            else:
                print(f"Question with frontendQuestionId {frontendQuestionId} updated successfully.")
        else:
            print(f"Question with frontendQuestionId {frontendQuestionId} not found.")
    
    except Exception as e:
        print(f"Error populating question model: {e}")
