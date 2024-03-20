import datetime
import jwt

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

User = get_user_model()


class JSONWebTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        try:
            payload = jwt.decode(key, settings.SECRET_KEY)
            user = User.objects.get(email=payload['email'])
        except (jwt.DecodeError, User.DoesNotExist):
            raise exceptions.AuthenticationFailed('Invalid token')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')
        return (user, payload)


class JWTTokenGenerator:
    def __init__(self, email):
        self.email = email

    def generate_token(self, minutes=0, hours=0, days=0):
        now = datetime.datetime.utcnow()
        payload = {
            'email': self.email,
            'iat': now,
            'nbf': now - datetime.timedelta(minutes=5),
            'exp': now + datetime.timedelta(minutes=minutes, hours=hours, days=days)
        }
        return jwt.encode(payload, settings.SECRET_KEY)


class AccessTokenGenerator(JWTTokenGenerator):
    def __init__(self, email):
        super().__init__(email)

    def generate_token(self):
        return super().generate_token(minutes=settings.JWT_ACCESS_TOKEN_MINUTES)


class RefreshTokenGenerator(JWTTokenGenerator):
    def __init__(self, email):
        super().__init__(email)

    def generate_token(self):
        return super().generate_token(hours=settings.JWT_REFRESH_TOKEN_DAYS)
