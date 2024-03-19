from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class Role(models.TextChoices):
    admin = "admin", "Администратор"
    staff = "staff", "Сотрудник"
    user = "user", "Пользователь"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(DjangoUserManager):
    def _create_user(self, email, password, commit=True, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, role=Role.admin, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(unique=True)
    role = models.CharField(
        choices=Role.choices,
        max_length=15,
        default=Role.user
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def is_staff(self):
        return self.role in (Role.admin, Role.staff)

    @property
    def is_superuser(self):
        return self.role == Role.admin

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
