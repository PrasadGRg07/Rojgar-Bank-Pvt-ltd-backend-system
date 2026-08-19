from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Super Admin"
        JOBSEEKER = "jobseeker", "Job Seeker"

    # Override email field
  #  email = models.EmailField(unique=True)
        
        

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    employee_id = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    # Verification via OTP
    is_verified = models.BooleanField(default=False)
    otp_hash = models.CharField(max_length=255, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.IntegerField(default=0)

    # Google OAuth
    google_id = models.CharField(max_length=255, blank=True, null=True)
    auth_provider = models.CharField(max_length=20, default='email')

    is_special_account = models.BooleanField(default=False, help_text="Grants unlimited access without changing the user's original role.")

    def __str__(self):
        return f"{self.username} ({self.role})"


class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    registration_data = models.JSONField()
    otp_hash = models.CharField(max_length=255, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending: {self.email}"