from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import leetcode_acc
from .tasks import *
from .serializers import *

class register_leetcode(APIView):

    def post(self, request, *args, **kwargs):
        leetcode_name = request.data.get('username')
        if leetcode_name is None or leetcode_name == "":
            return Response({"error": "Leetcode username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if leetcode_acc.objects.filter(leetcode_name=leetcode_name).exists():
            return Response({"error": "Leetcode user already exists"}, status=status.HTTP_400_BAD_REQUEST)
        acc = leetcode_acc.objects.create(leetcode_name=leetcode_name)

        get_user_data.delay(leetcode_name,acc.user)
        return Response({"message": "Leetcode user registered successfully"}, status=status.HTTP_201_CREATED)
    
class getLeetcodeInfo(APIView):
    def get(self, request,*args, **kwargs):
        leetcode_users = leetcode_acc.objects.all().order_by('-total_solved')
        serializer = leetcode_accSerializer(leetcode_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class getUserInfo(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if username is None or username == "":
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not leetcode_acc.objects.filter(leetcode_name=username).exists():
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        account = leetcode_acc.objects.get(leetcode_name=username)
        serializer = leetcode_accSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class getQuestionID(APIView):
    def get(self, request, *args, **kwargs):
        titleSlug = request.GET.get('titleSlug')
        if titleSlug is None or titleSlug == "":
            return Response({"error": "Title slug is required"}, status=status.HTTP_400_BAD_REQUEST)
        question_id = get_ques_id(titleSlug)

        return Response({"question_id": question_id}, status=status.HTTP_200_OK)
    
def get_today_questions(user):
    today = timezone.now()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    questions = Question.objects.filter(questionDate__range=(start_of_today, end_of_today))
    context = {'username':user}
    serializer = QuestionSerializer(questions, many=True, context=context)
    return serializer.data

class getQuestionsForTheDay(APIView):
    def get(self, request, *args, **kwargs):
        questions_data = get_today_questions(request.GET.get('username'))
        return Response(questions_data, status=status.HTTP_200_OK)



class debug_refresh_user_data(APIView):
    def get(self, request, *args, **kwargs):
        refresh_user_data.delay()
        return Response({"message": "Data refreshed"}, status=status.HTTP_200_OK)