from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from apps.employee.models import Job, EmployeeProfile

class EmployeeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="Password123!",
            first_name="Employer",
            last_name="One",
            role="employee"
        )
        # Obtain SimpleJWT tokens
        response = self.client.post(
            "/api/auth/login/",
            {"username": "employer", "password": "Password123!"},
            format="json"
        )
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_and_list_jobs(self):
        job_data = {
            "title": "Software Engineer",
            "experience": "2 years",
            "education": "Bachelor",
            "skills": ["Python", "Django"],
            "description": "Full stack role",
            "mainCategory": "IT",
            "subCategory": "Development",
            "openings": "3",
            "postingDate": "2026-07-08",
            "postingPeriod": "30 days",
            "jobLevel": "Mid",
            "district": "Kathmandu",
            "municipality": "Kathmandu MC",
            "specificLocation": "New Baneshwor",
            "workingTime": "Full-time",
            "currency": "NPR",
            "salaryPeriod": "Monthly",
            "salaryRange": "50k-80k",
            "gender": "Any",
            "license": "Required",
            "vehicle": "Required",
            "postToATS": True
        }

        # Test posting a job
        response = self.client.post("/api/employee/jobs/", job_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Software Engineer")
        self.assertEqual(response.data["skills"], ["Python", "Django"])
        self.assertTrue(response.data["postToATS"])

        # Test listing jobs
        response = self.client.get("/api/employee/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Software Engineer")

    def test_update_profile(self):
        profile_data = {
            "company_name": "Tech Corp",
            "address": "Baneshwor",
            "office_phone": "014444444",
            "official_email": "info@techcorp.com",
            "linkedin_id": "techcorp-in",
            "industry": "IT",
            "company_size": "11-50",
            "website": "https://techcorp.com",
            "facebook": "https://facebook.com/techcorp",
            "contact_person": "Jane Admin",
            "mobile": "9800000000",
            "intro": "Great place to work"
        }

        response = self.client.patch("/api/auth/update-profile/", profile_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "Tech Corp")
        self.assertEqual(response.data["address"], "Baneshwor")

        # Verify in database
        profile = EmployeeProfile.objects.get(user=self.user)
        self.assertEqual(profile.company_name, "Tech Corp")
        self.assertEqual(profile.address, "Baneshwor")
        self.assertEqual(profile.office_phone, "014444444")
        self.assertEqual(profile.official_email, "info@techcorp.com")
        self.assertEqual(profile.intro, "Great place to work")

    def test_change_password(self):
        # Invalid current password
        response = self.client.post(
            "/api/auth/change-password/",
            {"current_password": "WrongPassword!", "new_password": "NewPassword123!"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid password change
        response = self.client.post(
            "/api/auth/change-password/",
            {"current_password": "Password123!", "new_password": "NewPassword123!"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify can login with new password
        self.client.credentials()  # Clear auth headers
        response = self.client.post(
            "/api/auth/login/",
            {"username": "employer", "password": "NewPassword123!"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_mock_send_otp_and_update_email(self):
        # Send OTP
        response = self.client.post("/api/auth/send-otp/", {"phone": "9811111111"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "OTP sent successfully.")

        # Update Email
        response = self.client.post("/api/auth/update-email/", {"email": "new_email@example.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Email updated successfully.")
        
        # Verify db updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new_email@example.com")
