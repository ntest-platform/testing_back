from django.urls import path

from .views import CreateUserAPIView, JSONWebTokenAuth, RefreshTokenView, ChangePasswordAPIView

urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    path('token/', JSONWebTokenAuth.as_view()),
    path('refresh-token/', RefreshTokenView.as_view()),
    path('password/change/', ChangePasswordAPIView.as_view()),
]
