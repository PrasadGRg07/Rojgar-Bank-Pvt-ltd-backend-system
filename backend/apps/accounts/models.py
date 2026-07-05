from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    employee_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"