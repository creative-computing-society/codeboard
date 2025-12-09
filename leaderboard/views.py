import asyncio

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.utils import timezone
from asgiref.sync import sync_to_async
from adrf.views import APIView as AsyncAPIView

from .models import Leetcode, Question, Leaderboard
from .tasks import get_user_data, refresh_user_data
from .serializers import LeetCodeSerializer, QuestionSerializer


async def get_today_questions(username):
    today = timezone.now()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    async def fetch_questions():
        return await sync_to_async(list)(
            Question.objects.filter(questionDate__range=(start_of_today, end_of_today))
        )

    async def fetch_user():
        if not username:
            return None
        try:
            return await Leetcode.objects.aget(username=username)
        except Leetcode.DoesNotExist:
            return None

    # Run both concurrently
    questions, leetcode_acc_instance = await asyncio.gather(
        fetch_questions(), fetch_user()
    )

    serializer = QuestionSerializer(
        questions,
        many=True,
        context={"leetcode_acc_instance": leetcode_acc_instance},
    )
    return serializer.data


class Register(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        username = request.data.get("username")
        if not username:
            return Response(
                {"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        acc = Leetcode.objects.create(username=username, user=user)
        print(f"User {user} registered with Leetcode username {username}")
        if not acc:
            return Response(
                {"error": "User registration failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        get_user_data.delay(username, acc.pk)
        return Response(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        username = user.leetcode.username
        if not username:
            return Response(
                {"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = Leetcode.objects.get(username=username)
        except Leetcode.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeetCodeSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetQuestionsForTheDay(AsyncAPIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        try:
            user = request.user
            username = user.leetcode.username
            if not username:
                return Response(
                    {"error": "Username is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            questions_data = await get_today_questions(username)
            return Response(questions_data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response(
                {"error": "Questions not found"}, status=status.HTTP_404_NOT_FOUND
            )


class GetAllQuestions(AsyncAPIView):
    async def get(self, request, *args, **kwargs):
        username = request.query_params.get("username")

        async def fetch_questions():
            return await sync_to_async(list)(Question.objects.all())

        async def fetch_user():
            if not username:
                return None
            try:
                return await Leetcode.objects.aget(username=username)
            except Leetcode.DoesNotExist:
                return None

        questions, leetcode_acc_instance = await asyncio.gather(
            fetch_questions(), fetch_user()
        )

        serializer = QuestionSerializer(
            questions,
            many=True,
            context={"leetcode_acc_instance": leetcode_acc_instance},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class DailyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_day = Leaderboard.objects.get(leaderboard_type="daily").leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response(
                {"error": "Daily leaderboard not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(one_day, status=status.HTTP_200_OK)


class WeeklyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_week = Leaderboard.objects.get(
                leaderboard_type="weekly"
            ).leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response(
                {"error": "Weekly leaderboard not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(one_week, status=status.HTTP_200_OK)


class MonthlyLeaderboard(APIView):
    def get(self, request, *args, **kwargs):
        try:
            one_month = Leaderboard.objects.get(
                leaderboard_type="monthly"
            ).leaderboard_data
        except Leaderboard.DoesNotExist:
            return Response(
                {"error": "Monthly leaderboard not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(one_month, status=status.HTTP_200_OK)


class DebugRefreshUserData(APIView):
    def get(self, request, *args, **kwargs):
        refresh_user_data.delay()
        return Response(
            {"message": "Data refresh initiated"}, status=status.HTTP_200_OK
        )
