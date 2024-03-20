import jwt

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

User = get_user_model()


class JSONWebTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            payload = jwt.decode(key, settings.SECRET_KEY)
            user = User.objects.get(username=payload['username'])
        except (jwt.DecodeError, User.DoesNotExist):
            raise exceptions.AuthenticationFailed('Invalid token')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')
        return (user, payload)
