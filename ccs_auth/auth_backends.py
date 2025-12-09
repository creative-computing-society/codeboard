import os
import jwt
from dotenv import load_dotenv
from logging import getLogger

from django.contrib.auth.backends import BaseBackend
from django.db.models import Q as OR

from .models import CUser as CustomUser


load_dotenv()

JWT_SECRET = os.getenv("CLIENT_SECRET")
logger = getLogger(__name__)


class SSOAuthenticationBackend(BaseBackend):
    def authenticate(self, request, sso_token, *args, **kwargs):
        """Authenticate user using SSO token."""
        user_info = self.validate_sso_token(sso_token)
        if not user_info:
            return None

        email = user_info["email"]

        # Check if user already exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            first_name, last_name = user_info["name"].split(" ", 1)

            user = CustomUser.objects.create(
                id=user_info["_id"],
                email=email,
                first_name=first_name,
                last_name=last_name,
                roll_no=user_info["rollNo"],
            )
            logger.info("New user created via SSO: %s", user)

        return user

    def get_user(self, user_id):
        try:
            # Using models build in OR operator to make 2 db calls into 1 :o
            # Found this operator randomly while going through django's repo lol
            return CustomUser.objects.filter(OR(id=user_id) | OR(email=user_id)).first()
        except CustomUser.DoesNotExist:
            return None

    def validate_sso_token(self, sso_token):
        try:
            payload = jwt.decode(sso_token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
