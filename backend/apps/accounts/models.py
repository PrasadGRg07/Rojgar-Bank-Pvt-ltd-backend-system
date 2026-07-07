from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Super Admin"
        
        

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    employee_id = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"