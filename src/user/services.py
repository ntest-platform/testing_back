from datetime import timedelta
import secrets
import string

from django.utils import timezone
from rest_framework import status

from .managers import PasswordResetCodeManager, UserRepository


class PasswordChangeService:
    def __init__(self, user_instance):
        self.user = user_instance

    def execute(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if self.user.check_password(old_password):
            self.user.set_password(new_password)
            self.user.save()
            return {'message': 'Password changed successfully.'}, status.HTTP_200_OK
        return {'error': 'Incorrect old password.'}, status.HTTP_400_BAD_REQUEST


class PasswordCodeService:
    @staticmethod
    def generate_code(code_length=8):
        code_characters = string.ascii_letters + string.digits
        code = ''.join(secrets.choice(code_characters) for _ in range(code_length))
        return code

    @classmethod
    def create_code(cls, user, code_length=8, expiration_hours=12):
        PasswordResetCodeManager.delete_user_code(user)
        code = cls.generate_code(code_length)
        now = timezone.now().astimezone(timezone.get_current_timezone())
        expired_at = now + timedelta(hours=expiration_hours)
        return PasswordResetCodeManager.create_reset_code(user, code, expired_at)

    @classmethod
    def confirm_code(cls, user, code):
        now = timezone.now().astimezone(timezone.get_current_timezone())
        code_object = PasswordResetCodeManager.get_reset_code(user)
        PasswordResetCodeManager.delete_user_code(user)

        if code_object.recover_code != code:
            raise ValueError("Invalid code")

        if code_object.expired_at < now:
            raise ValueError("The code's lifetime has expired")


class PasswordForgiveService:
    @staticmethod
    def execute(data):
        email = data.get('email')

        try:
            user = UserRepository.get_user_by_email(email)
            PasswordCodeService.create_code(user)
            return {'message': 'Password changed successfully.'}, status.HTTP_200_OK
        except Exception as e:
            return {'error': str(e)}, status.HTTP_400_BAD_REQUEST


class PasswordResetService:
    @staticmethod
    def execute(data):
        email = data.get('email')
        recover_code = data.get('recover_code')
        new_password = data.get('new_password')

        try:
            user = UserRepository.get_user_by_email(email)
            PasswordCodeService.confirm_code(user, recover_code)
            user.set_password(new_password)
            user.save()
            return {'message': 'Password changed successfully.'}, status.HTTP_200_OK
        except Exception as e:
            return {'error': str(e)}, status.HTTP_400_BAD_REQUEST
