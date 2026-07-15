from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Leetcode, Question, Leaderboard
from .tasks import *
from .serializers import LeetCodeSerializer, QuestionSerializer

def get_today_questions(username):
    today = timezone.now()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    questions = Question.objects.filter(questionDate__range=(start_of_today, end_of_today))
    context = {'username': username}
    serializer = QuestionSerializer(questions, many=True, context=context)
    return serializer.data

class Profile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            username = user.leetcode.username
        except:
            return Response({"error": "Username is required"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            account = Leetcode.objects.get(username=username)
        except Leetcode.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeetCodeSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetQuestionsForTheDay(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            try:
                username = user.leetcode.username
            except:
                return Response({"error": "Username is required"}, status=status.HTTP_404_NOT_FOUND)
            questions_data = get_today_questions(username)
            return Response(questions_data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"error": "Questions not found"}, status=status.HTTP_404_NOT_FOUND)
        

class GetAllQuestions(APIView):
    def get(self, request, *args, **kwargs):
        try:
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"error": "Questions not found"}, status=status.HTTP_404_NOT_FOUND)

class DailyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_day = Leaderboard.objects.get(leaderboard_type='daily').leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response({"error": "Daily leaderboard not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(one_day, status=status.HTTP_200_OK)

class WeeklyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_week = Leaderboard.objects.get(leaderboard_type='weekly').leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response({"error": "Weekly leaderboard not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(one_week, status=status.HTTP_200_OK)

class MonthlyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_month = Leaderboard.objects.get(leaderboard_type='monthly').leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response({"error": "Monthly leaderboard not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(one_month, status=status.HTTP_200_OK)

class DebugRefreshUserData(APIView):
    def get(self, request, *args, **kwargs):
        refresh_user_data.delay()
        return Response({"message": "Data refresh initiated"}, status=status.HTTP_200_OK)


