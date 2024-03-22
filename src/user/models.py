from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    """

    class Role(models.TextChoices):
        admin = "admin", "Администратор"
        staff = "staff", "Сотрудник"
        user = "user", "Пользователь"

    email = models.EmailField(max_length=40, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(
        choices=Role.choices,
        max_length=15,
        default=Role.user
    )

    @property
    def is_staff(self):
        return self.role in (self.Role.admin, self.Role.staff)

    @property
    def is_superuser(self):
        return self.role == self.Role.admin

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recover_code = models.CharField(max_length=10)
    expired_at = models.DateTimeField()
