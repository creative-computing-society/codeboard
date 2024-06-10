from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from .models import leetcode_acc
from .fetch_leetcode_data import get_user_data

class register_leetcode(APIView):

    def post(self, request, *args, **kwargs):
        leetcode_name = request.data.get('leetcode_name')
        if leetcode_name is None or leetcode_name == "":
            return Response({"error": "Leetcode name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if leetcode_acc.objects.filter(leetcode_name=leetcode_name).exists():
            return Response({"error": "Leetcode user already exists"}, status=status.HTTP_400_BAD_REQUEST)
        acc = leetcode_acc.objects.create(leetcode_name=leetcode_name)
        get_user_data(leetcode_name,acc.user)

        return Response({"message": "Leetcode user registered successfully"}, status=status.HTTP_201_CREATED)
    
class getLeetcodeInfo(APIView):
    def get(self, request,*args, **kwargs):
        result = []
        leetcode_users = leetcode_acc.objects.all().order_by('-number_of_questions')
        for account in leetcode_users:
            d={
                'serial': account.user,
                'leetcode_name': account.leetcode_name,
                'name': account.name,
                'rank': account.rank,
                'photo_url': account.photo_url,
                'number_of_questions': account.number_of_questions,
                'last_solved': account.last_solved
            }
            result.append(d)
        return Response(result, status=status.HTTP_200_OK)

class getUserInfo(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if username is None or username == "":
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not leetcode_acc.objects.filter(leetcode_name=username).exists():
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        account = leetcode_acc.objects.get(leetcode_name=username)
        result = {
            'serial': account.user,
            'leetcode_name': account.leetcode_name,
            'name': account.name,
            'rank': account.rank,
            'photo_url': account.photo_url,
            'number_of_questions': account.number_of_questions,
            'last_solved': account.last_solved
        }
        return Response(result, status=status.HTTP_200_OK)