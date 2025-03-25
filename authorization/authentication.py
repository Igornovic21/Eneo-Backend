import six
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except:
            raise AuthenticationFailed('Invalid token')
        
        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or delete')
                
        if token.created < timezone.now() - settings.TOKEN_EXPIRE_TIME:
            raise AuthenticationFailed('Token as expired')

        return token.user, token

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
        
account_activation_token = TokenGenerator()
