import datetime
import json
import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient

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


class PasswordChangeServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='test_user', email='test@example.com', password='old_password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_password_change_incorrect_old_password(self):
        data = {'old_password': 'wrong_password', 'new_password': 'new_password'}
        response = self.client.post(
            '/user/password/change/', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Incorrect old password.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))

    def test_password_change_success(self):
        data = {'old_password': 'old_password', 'new_password': 'new_password'}
        response = self.client.post(
            '/user/password/change/', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password changed successfully.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))


class PasswordResetServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='test_user', email='test@example.com', password='old_password')
        self.client = APIClient()

    def test_password_forgive_success(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(
            '/user/password/forgive/', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password changed successfully.')

    def test_password_forgive_invalid_email(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(
            '/user/password/forgive/', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_password_reset_invalid_code(self):
        data = {'email': 'test@example.com', 'recover_code': 'invalid_code', 'new_password': 'new_password'}
        response = self.client.post(
            '/user/password/reset/', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
