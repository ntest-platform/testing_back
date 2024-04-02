from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password=password, role=self.model.Role.admin, **extra_fields)


class PasswordResetCodeManager:
    @staticmethod
    def create_reset_code(user, recover_code, expired_at):
        from .models import PasswordResetCode
        return PasswordResetCode.objects.create(user=user, recover_code=recover_code, expired_at=expired_at)

    @staticmethod
    def get_reset_code(user):
        from .models import PasswordResetCode
        reset_code_obj = PasswordResetCode.objects.filter(user=user).order_by('-expired_at').first()

        if not reset_code_obj:
            raise ValueError("There is no code")

        return reset_code_obj

    @staticmethod
    def delete_user_code(user):
        from .models import PasswordResetCode
        reset_code_list = PasswordResetCode.objects.filter(user=user)

        for reset_code in reset_code_list:
            reset_code.delete()


class UserRepository:
    @staticmethod
    def get_user_by_email(user_email):
        User = get_user_model()
        user_obj = User.objects.filter(email=user_email).first()

        if not user_obj:
            raise ValueError("There is no user")

        return user_obj
