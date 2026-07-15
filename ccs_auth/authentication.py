from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.conf import settings
import datetime

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')
        
        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')
        
        utc_now = datetime.datetime.now()
        if token.created < utc_now - datetime.timedelta(seconds=settings.TOKEN_EXPIRY):
            raise AuthenticationFailed('Token has expired.')
        
        return token.user, token
