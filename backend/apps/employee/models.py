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

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    # ==========================
    # Owner
    # ==========================
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    # ==========================
    # Basic Information
    # ==========================
    title = models.CharField(max_length=255)

    main_category = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)

    employment_type = models.CharField(max_length=100, blank=True)
    job_level = models.CharField(max_length=100, blank=True)

    openings = models.PositiveIntegerField(default=1)

    workplace = models.CharField(max_length=100, blank=True)

    department = models.CharField(max_length=150, blank=True)
    job_code = models.CharField(max_length=100, blank=True)

    # ==========================
    # Job Description
    # ==========================
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)

    responsibilities = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    why_join_us = models.TextField(blank=True)

    # ==========================
    # Requirements
    # ==========================
    experience = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=255, blank=True)

    skills = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)

    license = models.CharField(max_length=100, blank=True)
    vehicle = models.CharField(max_length=100, blank=True)

    gender = models.CharField(max_length=50, blank=True)

    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)

    # ==========================
    # Salary
    # ==========================
    currency = models.CharField(max_length=20, default="NPR")

    salary_type = models.CharField(max_length=50, blank=True)

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    negotiable = models.BooleanField(default=False)
    hide_salary = models.BooleanField(default=False)

    # ==========================
    # Location
    # ==========================
    province = models.CharField(max_length=100, blank=True)

    district = models.CharField(max_length=100, blank=True)

    municipality = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=255, blank=True)

    work_mode = models.CharField(max_length=100, blank=True)

    map_link = models.URLField(blank=True)

    travel_required = models.BooleanField(default=False)

    # ==========================
    # Benefits
    # ==========================
    benefits = models.JSONField(default=list, blank=True)

    other_benefits = models.TextField(blank=True)

    # ==========================
    # Application
    # ==========================
    application_deadline = models.DateField(
        null=True,
        blank=True,
    )

    joining_date = models.DateField(
        null=True,
        blank=True,
    )

    contact_email = models.EmailField(blank=True)

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    required_documents = models.JSONField(
        default=list,
        blank=True,
    )

    accept_until_filled = models.BooleanField(default=False)

    send_confirmation_email = models.BooleanField(default=True)

    allow_quick_apply = models.BooleanField(default=True)

    # ==========================
    # Posting
    # ==========================
    posting_date = models.DateField(
        null=True,
        blank=True,
    )

    posting_period = models.CharField(
        max_length=100,
        blank=True,
    )

    post_to_ats = models.BooleanField(default=False)

    # ==========================
    # Admin Review
    # ==========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_jobs",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    # ==========================
    # Timestamps
    # ==========================
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
  