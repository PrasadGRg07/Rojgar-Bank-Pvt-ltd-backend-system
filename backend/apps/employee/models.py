from django.conf import settings
from django.db import models
from apps.accounts.models import CustomUser


    
class EmployeeProfile(models.Model):# for the employee profile, we will use a one-to-one relationship with the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(null=True, blank=True)

    # New fields for registration
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.company_name}"