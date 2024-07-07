from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv

from leaderboard.models import Leetcode
from leaderboard.tasks import get_user_data, fetch_user_profile
from .serializers import *
from .models import *

import os, requests
load_dotenv()

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        sso_token = request.data.get('token')
        user = authenticate(request, sso_token=sso_token)
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        print(f"User {user} logged in successfully with ID: {user.pk}")

        token, _ = Token.objects.get_or_create(user=user)
        serializer = CUserSerializer(instance=user)

        # If the user has a leetcode account, return leetcode true with response
        if user.leetcode:
            return Response({'token': token.key, 'user': serializer.data, 'leetcode': True}, status=status.HTTP_200_OK)

        return Response({'token': token.key, 'user': serializer.data, 'leetcode': False}, status=status.HTTP_200_OK)

class RegisterLeetcode(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        leetcode_username = request.data.get('leetcode_username')
        user = request.user
        if not leetcode_username:
            return Response({'error': 'Leetcode username is required'}, status=status.HTTP_400_BAD_REQUEST)
        acc = Leetcode.objects.create(username=leetcode_username, user=user)
        if not acc:
            return Response({'error': 'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)
        get_user_data.delay(leetcode_username, acc.pk)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

class VerifyLeetcode(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        username = request.data.get('leetcode_username')
        if not username:
            return Response({'error': 'Leetcode username is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            a = Leetcode.objects.get(username=username)
            return Response({'error': 'User registered on codeboard'}, status=status.HTTP_400_BAD_REQUEST)
        except Leetcode.DoesNotExist:
            pass

        user_data = fetch_user_profile(username)
        if user_data:
            return Response(user_data, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        token =Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)