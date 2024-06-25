from django.contrib.auth.backends import BaseBackend
from .models import CUser as CustomUser
from dotenv import load_dotenv
import os, jwt
load_dotenv()

class SSOAuthenticationBackend(BaseBackend):
    def authenticate(self, request, sso_token=None):
        if sso_token is None:
            return None

        user_info = self.validate_sso_token(sso_token)
        if user_info:
            try:
                user = CustomUser.objects.get(pk=user_info['email'])
            except CustomUser.DoesNotExist:
                first_name, last_name = user_info['name'].split(' ')
                print("authentication backend: ", user_info)
                user = CustomUser.objects.create(
                    id=user_info['_id'],
                    email=user_info['email'],
                    first_name=first_name,
                    last_name=last_name,
                    roll_no=user_info['rollNo']
                )
                print("authentication backend: ", user)
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except:
            pass
        try:
            return CustomUser.objects.get(email=user_id)
        except CustomUser.DoesNotExist:
            return None

    def validate_sso_token(self, sso_token):
        jwt_secret = os.getenv('CLIENT_SECRET')
        try:
            payload = jwt.decode(sso_token, jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
