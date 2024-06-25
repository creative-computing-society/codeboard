from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import *

class CUserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CUser
        fields = ('id', 'email', 'first_name', 'last_name','roll_no')

    def create(self, validated_data):
        user = super().create(validated_data)
        Token.objects.create(user=user)
        return user
    