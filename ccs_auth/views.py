import asyncio
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate, login
from adrf.views import APIView as AsyncAPIView
from dotenv import load_dotenv
from logging import getLogger

from leaderboard.models import Leetcode
from leaderboard import get_session

from .serializers import CUserSerializer

load_dotenv()

API_URL = "http://127.0.0.1:8000/api/leaderboard"

logger = getLogger(__name__)


class LoginView(AsyncAPIView):
    async def post(self, request):
        sso_token = request.data.get("token")
        leetcode_username = request.data.get("leetcode_username")

        # Authenticate user
        user = await asyncio.to_thread(
            authenticate, request, sso_token=sso_token
        )  # authenticate() does DB + hashing, which will block event loop
        if not user:
            return Response(
                {"error": "Invalid Credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log user in
        await asyncio.to_thread(login, request, user)  # login() is also blocking

        logger.info(f"User {user} logged in successfully with ID: {user.pk}")

        # Get token and aiohttp session
        (token, _), session = await asyncio.gather(
            Token.objects.aget_or_create(user=user),
            get_session(),
        )

        # If user already has a linked Leetcode account, return early
        serializer = CUserSerializer(instance=user)
        if hasattr(user, "leetcode"):
            return Response(
                {"token": token.key, "user": serializer.data},
                status=status.HTTP_200_OK,
            )

        # Require Leetcode username if not linked
        if not leetcode_username:
            return Response(
                {
                    "error": "Leetcode username is required",
                    "message": "Please provide a Leetcode username to link to your account",
                    "leetcode": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check existence + try API registration in parallel
        async def register_leetcode():
            async with session.post(
                f"{API_URL}/register/",
                data={"username": leetcode_username},
                headers={"Authorization": f"Token {token.key}"},
            ) as resp:
                return resp.status

        user_exists, status_code = await asyncio.gather(
            Leetcode.objects.filter(username=leetcode_username).aexists(),
            register_leetcode(),
        )

        if user_exists:
            return Response(
                {"error": "Leetcode account already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Link Leetcode account if registration succeeded
        if status_code in (200, 201):
            logger.info("Registration request successful")
            leetcode_acc = await Leetcode.objects.filter(
                username=leetcode_username
            ).afirst()
            if leetcode_acc:
                user.leetcode = leetcode_acc
                await user.asave()

        # Return success response
        return Response(
            {"token": token.key, "user": serializer.data},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
