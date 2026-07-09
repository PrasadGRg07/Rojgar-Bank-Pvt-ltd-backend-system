from django.conf import settings
from django.db import models
from apps.accounts.models import CustomUser


    
class EmployeeProfile(models.Model): # for the employee profile, we will use a one-to-one relationship with the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(null=True, blank=True)

    # New fields for registration
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Additional profile details from the frontend settings forms
    address = models.CharField(max_length=255, blank=True)
    office_phone = models.CharField(max_length=20, blank=True)
    official_email = models.EmailField(blank=True)
    linkedin_id = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    intro = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.company_name or 'No Company'}"


class Job(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    experience = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=255, blank=True)
    skills = models.JSONField(default=list, blank=True)
    description = models.TextField()
    main_category = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)
    openings = models.CharField(max_length=50, blank=True)
    posting_date = models.CharField(max_length=100, blank=True)
    posting_period = models.CharField(max_length=100, blank=True)
    job_level = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    specific_location = models.CharField(max_length=255, blank=True)
    working_time = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=20, blank=True)
    salary_period = models.CharField(max_length=100, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    license = models.CharField(max_length=100, blank=True)
    vehicle = models.CharField(max_length=100, blank=True)
    post_to_ats = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title