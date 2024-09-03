from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.contrib.auth.backends import BaseBackend
from .models import CUser as CustomUser
from dotenv import load_dotenv
import os, jwt, json
load_dotenv()

class SSOAuthenticationBackend(BaseBackend):
    def authenticate(self, request, sso_token=None):
        if sso_token is None:
            return None

        user_info = self.validate_sso_token(sso_token)
        if user_info:
            try:
                user = CustomUser.objects.get(pk=user_info['email'])
                # Check and update user information if different
                name_parts = user_info.get('name', '').split(' ')
                has_changes = False

                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                elif len(name_parts) == 1:
                    first_name = name_parts[0]
                    last_name = ''
                else:
                    first_name = ''
                    last_name = ''

                if user.first_name != first_name:
                    user.first_name = first_name
                    has_changes = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    has_changes = True

                if 'rollNo' in user_info and user.roll_no != user_info['rollNo']:
                    user.roll_no = user_info['rollNo']
                    has_changes = True
                if 'branch' in user_info and user.branch != user_info['branch']:
                    user.branch = user_info['branch']
                    has_changes = True
                if has_changes:
                    user.save()
            except CustomUser.DoesNotExist:
                # Safely handle the name split here as well
                name_parts = user_info.get('name', '').split(' ')
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                elif len(name_parts) == 1:
                    first_name = name_parts[0]
                    last_name = ''
                else:
                    first_name = ''
                    last_name = ''

                print("authentication backend: ", user_info)
                try:
                    roll_no = user_info.get('rollNo', '')
                    branch = user_info.get('branch', '')
                except:
                    roll_no = ''
                    branch = ''

                user = CustomUser.objects.create(
                    id=user_info['_id'],
                    email=user_info['email'],
                    first_name=first_name,
                    last_name=last_name,
                    roll_no=roll_no,
                    branch=branch
                )
            return user
        return None


def decrypt(encrypted_data, key):
    # Ensure the key is 96 characters long
    if len(key) != 96:
        raise ValueError('Key must be exactly 96 characters long')

    # Split the IV and the encrypted data
    iv = bytes.fromhex(encrypted_data[:32])  # First 32 hex characters correspond to the 16 bytes IV
    encrypted_data = bytes.fromhex(encrypted_data[32:])

    # Extract the encryption key (first 32 characters)
    encryption_key = key[:32].encode('utf-8')

    # Create a Cipher object using AES-256-CBC
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    # print("Decrypted data:", decrypted_data)

    try:
        # Remove padding bytes
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        clean_data = unpadder.update(decrypted_data) + unpadder.finalize()
        json_string = clean_data.decode('utf-8')

        # Decode the decrypted data to a UTF-8 string and then parse it as JSON
        decrypted_json = json.loads(json_string)
        # print("Decrypted JSON:", decrypted_json)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print("Decrypted data that caused the error:", decrypted_data)
        raise

    # Return the decrypted JSON object
    return decrypted_json

