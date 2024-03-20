from django.urls import path

from .views import CreateUserAPIView, JSONWebTokenAuth

urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    path('token/', JSONWebTokenAuth.as_view()),
]
