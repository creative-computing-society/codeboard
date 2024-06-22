from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import leetcode_acc, Question, Leaderboard
from ccs_auth.models import CUser
from .tasks import get_user_data, refresh_user_data
from .serializers import leetcode_accSerializer, QuestionSerializer

def get_today_questions(user):
    today = timezone.now()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    questions = Question.objects.filter(questionDate__range=(start_of_today, end_of_today))
    context = {'username': user}
    serializer = QuestionSerializer(questions, many=True, context=context)
    return serializer.data

class RegisterLeetcode(APIView):
    def post(self, request, *args, **kwargs):
        leetcode_name = request.data.get('username')
        ccs_user_id = request.data.get('ccs_user')

        if not ccs_user_id:
            return Response({"error": "CCS user ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        ccs_user = get_object_or_404(CUser, pk=ccs_user_id)

        if not leetcode_name or leetcode_name == '':
            return Response({"error": "Leetcode username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if leetcode_acc.objects.filter(username=leetcode_name).exists():
            return Response({"error": "Leetcode user already exists"}, status=status.HTTP_200_OK)
        
        acc = leetcode_acc.objects.create(username=leetcode_name, user=ccs_user)
        get_user_data.delay(leetcode_name, acc.pk)
        
        return Response({"message": "Leetcode user registered successfully"}, status=status.HTTP_201_CREATED)

class GetLeetcodeInfo(APIView):
    def get(self, request, *args, **kwargs):
        leetcode_users = leetcode_acc.objects.all().order_by('-total_solved')
        serializer = leetcode_accSerializer(leetcode_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetUserInfo(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            account = leetcode_acc.objects.get(username=username)
        except leetcode_acc.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = leetcode_accSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetQuestionsForTheDay(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        questions_data = get_today_questions(username)
        return Response(questions_data, status=status.HTTP_200_OK)

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
