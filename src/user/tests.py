import datetime
import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class JSONWebTokenAuthTests(APITestCase):
    def test_obtain_jwt_tokens(self):
        user = User.objects.create_user(first_name='testuser', email='test@example.com', password='password')
        data = {'email': 'test@example.com', 'password': 'password'}
        response = self.client.post('/user/token/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_obtain_jwt_tokens_invalid_credentials(self):
        data = {'email': 'nonexistent@example.com', 'password': 'password'}
        response = self.client.post('/user/token/', data, format='json')
        self.assertEqual(response.status_code, 400)


class RefreshTokenViewTests(APITestCase):
    def test_refresh_token(self):
        user = User.objects.create_user(first_name='testuser', email='test@example.com', password='password')
        payload = {'email': user.email}
        refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        data = {'refresh_token': refresh_token}
        response = self.client.post('/user/refresh-token/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)

    def test_refresh_token_expired(self):
        now = datetime.datetime.utcnow()
        payload = {'exp': now - datetime.timedelta(minutes=5)}
        expired_refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        data = {'refresh_token': expired_refresh_token}
        response = self.client.post('/user/refresh-token/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_refresh_token_invalid(self):
        invalid_refresh_token = 'invalid_token'
        data = {'refresh_token': invalid_refresh_token}
        response = self.client.post('/user/refresh-token/', data, format='json')
        self.assertEqual(response.status_code, 401)


class CreateUserAPIViewTests(APITestCase):
    def test_create_user(self):
        data = {'first_name': 'testuser', 'email': 'test@example.com', 'password': 'password'}
        response = self.client.post('/user/create/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_user_invalid_data(self):
        invalid_data = {'first_name': 'testuser', 'password': 'password'}
        response = self.client.post('/user/create/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
