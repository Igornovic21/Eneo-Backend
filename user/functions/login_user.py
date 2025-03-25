from django.contrib.auth.models import update_last_login

from user.models import User
from user.functions.check_token import token_expire_handler, expires_in

from rest_framework.authtoken.models import Token

def login_user(account:User) -> dict:
    token, _ = Token.objects.get_or_create(user = account)
    token = token_expire_handler(token)
    update_last_login(None, account)
    return {
        'expired_in': expires_in(token),
        'token': token.key
    }
    