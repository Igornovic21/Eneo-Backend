from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from rest_framework.authtoken.models import Token

def expires_in(token):
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time

def is_token_expired(token):
    return expires_in(token) < timedelta(seconds = 0)

def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user = token.user)
    return token
