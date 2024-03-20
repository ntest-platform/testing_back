from django.urls import path

from .views import CreateUserAPIView

urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
]
