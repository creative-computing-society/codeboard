from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

import jwt
'''For Testing, To be removed later'''
class SignUPView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token': token.key, 'user':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(instance=user)
        return Response({'token': token.key, 'user':serializer.data}, status=status.HTTP_201_CREATED)

'''Code to keep the user logged in using JWT'''
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
class TestToken(APIView):
    def get(self, request):
        return Response({'message': 'passed for {}'.format(request.user.name)})
    
class SignUpTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        try:
            jwt_secret = 'secret'
            if token is None:
                return Response({'error': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)
            # try:
            #     payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            # except jwt.ExpiredSignatureError:
            #     return Response({'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
            # except jwt.InvalidTokenError:
            #     return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            payload = request.data
            email = payload['email']
            name = payload['name']
            user = get_object_or_404(CUser, email=email, name=name)
            if user is None:
                serializer = CUserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    if CUser.objects.filter(email=request.data['email']).exists():
                        user = CUser.objects.get(email=request.data['email'])
                    else:
                        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
                    user.set_password(request.data['password'])
                    user.save()
                    token = Token.objects.create(user=user)
                    return Response({'token': token.key, 'user':serializer.data}, status=status.HTTP_201_CREATED)
        except:        
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        try:
            jwt_secret = 'secret'
            if token is None:
                return Response({'error': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)
            '''This code is to implement CCS authentication using JWT'''
            # try:
            #     payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            # except jwt.ExpiredSignatureError:
            #     return Response({'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
            # except jwt.InvalidTokenError:
            #     return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            payload = request.data
            email = payload['email']
            name = payload['name']

            user = get_object_or_404(CUser, email=email, name=name)
            if user is None:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            serializer = CUserSerializer(instance=user)
            return Response({'token': token.key, 'user':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
class LogoutView(APIView):
    def get(self, request):
        token =Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)