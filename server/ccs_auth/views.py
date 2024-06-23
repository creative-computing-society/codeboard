from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv

from leaderboard.models import Leetcode
from .serializers import *
from .models import *

import os, requests
load_dotenv()

API_URL = 'http://127.0.0.1:8000/api/leaderboard/'

class LoginView(APIView):
    def post(self, request):
        sso_token = request.data.get('token')
        leetcode_username = request.data.get('leetcode_username')

        # Authenticate user with SSO token
        user = authenticate(request, sso_token=sso_token)
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # Login user
        login(request, user)
        print(f"User {user} logged in successfully with ID: {user.pk}")

        # Generate or retrieve token for the user
        token, _ = Token.objects.get_or_create(user=user)

        # Serialize user data
        serializer = CUserSerializer(instance=user)

        try:
            # Check if the user already has a linked Leetcode account
            leetcode = user.leetcode
            print(f"Leetcode account already exists for {user} as {leetcode.username}")
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        except Leetcode.DoesNotExist:
            print(f"Leetcode account does not exist for {user}")
            if not leetcode_username:
                return Response({'error': 'Leetcode username is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the provided Leetcode username already exists
            if Leetcode.objects.filter(username=leetcode_username).exists():
                return Response({'error': 'Leetcode account already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Attempt to register the Leetcode account via API
            res = requests.post(
                f"{API_URL}/register/",
                data={'username': leetcode_username},
                headers={"Authorization": f"Token {token.key}"}
            )
            
            if res.status_code == 200 or res.status_code == 201:
                print("Registration request successful")
                user.leetcode = Leetcode.objects.filter(username=leetcode_username).first()
            else:
                print(f"Registration request failed: {res.status_code} - {res.text}")

        except Exception as e:
            print(f"Error making request to /register/: {e}")

        # Save user with updated Leetcode account reference if created
        user.save()

        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        token =Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)