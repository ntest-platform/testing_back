from django.urls import path

from .views import (
    CreateUserAPIView, JSONWebTokenAuth, RefreshTokenView,
    PasswordChangeAPIView, PasswordForgiveAPIView, PasswordResetAPIView
)

urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    path('token/', JSONWebTokenAuth.as_view()),
    path('refresh-token/', RefreshTokenView.as_view()),
    path('password/change/', PasswordChangeAPIView.as_view()),
    path('password/forgive/', PasswordForgiveAPIView.as_view()),
    path('password/reset/', PasswordResetAPIView.as_view()),
]
