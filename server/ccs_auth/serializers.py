from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CUser
class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ('id', 'username','password' ,'email')

class CUserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CUser
        fields = ('id', 'email', 'password', 'name', 'is_superuser')

    def create(self, validated_data):
        if validated_data.get('is_superuser', False):
            user = CUser.objects.create_superuser(
                email=validated_data['email'],
                password=validated_data['password'],
                name=validated_data['name'],
            )
        else:
            user = CUser.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                name=validated_data['name']
            )
        return user
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['password'] = instance.password
        return ret