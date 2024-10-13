import logging
import secrets
import os
import jwt
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import make_password, check_password
from .models import CUser as CustomUser
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SSOAuthenticationBackend(BaseBackend):
    def authenticate(self, request, sso_token=None, email=None, password=None):
        user = None
        
        # Handle SSO Token Authentication
        if sso_token:
            user_info = self.validate_sso_token(sso_token)
            if user_info:
                user = self.get_or_create_user(user_info)

        # Handle Password Authentication
        if email and password:
            user = self.authenticate_password(email, password)

        return user

    def get_or_create_user(self, user_info):
        email = user_info['email']
        try:
            user = CustomUser.objects.get(email=email)
            self.update_user_info(user, user_info)

            # Check if the user has a password
            if not user.password or user.password == "":
                strong_password = secrets.token_urlsafe(16)
                user.password = make_password(strong_password)
                user.login_password = strong_password
                user.save()
                logger.info(f"Generated strong password for existing user {email}. Consider sending it securely.")

                
            logger.debug(f"Found existing user: {email}")
            return user
        except CustomUser.DoesNotExist:
            return self.create_new_user(user_info)

    def authenticate_password(self, email, password):
        try:
            user = CustomUser.objects.get(email=email)
            if user:
                if check_password(password, user.password):
                    logger.debug(f"User {email} authenticated successfully.")
                    return user
                logger.warning(f"Invalid password for user {email}.")
        except CustomUser.DoesNotExist:
            logger.warning(f"User with email {email} not found.")
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            logger.warning(f"User with id {user_id} not found by ID.")
        try:
            return CustomUser.objects.get(email=user_id)
        except CustomUser.DoesNotExist:
            logger.warning(f"User with email {user_id} not found by email.")
            return None

    def validate_sso_token(self, sso_token):
        jwt_secret = os.getenv('CLIENT_SECRET')
        try:
            payload = jwt.decode(sso_token, jwt_secret, algorithms=['HS256'], leeway=10)
            decrypted_data = self.decrypt(payload['ex'], jwt_secret)
            logger.debug("SSO token successfully validated and decrypted.")
            return decrypted_data
        except jwt.ExpiredSignatureError:
            logger.warning("SSO token has expired.")
        except jwt.InvalidTokenError:
            logger.warning("SSO token is invalid.")
        return None

    def update_user_info(self, user, user_info):
        name_parts = user_info.get('name', '').split(' ')
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        roll_no = user_info.get('rollNo', '')
        branch = user_info.get('branch', '')

        changes = any([
            user.first_name != first_name,
            user.last_name != last_name,
            user.roll_no != roll_no,
            user.branch != branch
        ])

        if changes:
            user.first_name = first_name
            user.last_name = last_name
            user.roll_no = roll_no
            user.branch = branch
            user.save()
            logger.info(f"Updated user info for {user_info['email']}")

    def create_new_user(self, user_info):
        strong_password = secrets.token_urlsafe(16)
        name_parts = user_info.get('name', '').split(' ')
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        user = CustomUser.objects.create(
            id=user_info['_id'],
            email=user_info['email'],
            first_name=first_name,
            last_name=last_name,
            roll_no=user_info.get('rollNo', ''),
            branch=user_info.get('branch', ''),
            password=make_password(strong_password),
            login_password=strong_password
        )
        logger.debug(f"Generated strong password for new user {user_info['email']}")
        return user

    def decrypt(self, encrypted_data, key):
        if len(key) < 32:
            raise ValueError('Key must be at least 32 characters long for AES-256 encryption.')

        iv = bytes.fromhex(encrypted_data[:32])
        encrypted_data = bytes.fromhex(encrypted_data[32:])
        encryption_key = key[:32].encode('utf-8')

        cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        try:
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            clean_data = unpadder.update(decrypted_data) + unpadder.finalize()
            decrypted_json = json.loads(clean_data.decode('utf-8'))
            logger.debug("Data decrypted and parsed successfully.")
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON during decryption.")
            raise
        except Exception as e:
            logger.exception("Unexpected error during decryption.")
            raise

        return decrypted_json
