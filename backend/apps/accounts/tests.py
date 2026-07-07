from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="jane",
            email="jane@example.com",
            password="Secret123!",
            first_name="Jane",
            last_name="Doe",
        )

    def test_login_with_email_is_accepted(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "jane@example.com", "password": "Secret123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
