from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv

from .serializers import *
from .models import *

import os, requests
load_dotenv()

api_url = os.getenv('API_URL')

class LoginView(APIView):
    def post(self, request):
        sso_token = request.data.get('token')
        leetcode_username = request.data.get('leetcode_username')
        user = authenticate(request, sso_token=sso_token)
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            serializer = CUserSerializer(instance=user)
            res = requests.post(api_url+'register_user/', data={'ccs_user': user.pk, 'username': leetcode_username})
            if res.status_code not in [200, 201]:
                return Response({'error': 'Invalid leetcode username'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'token': token.key, 'user':serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        token =Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)