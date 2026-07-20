from django.conf import settings
from django.db import models


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobseeker_profile",
    )

    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True,
    )

    bio = models.TextField(blank=True)


    portfolio = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

#================Skills==============
class Skill(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="skills",
    )

    name = models.CharField(max_length=100)

    level = models.CharField(
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return self.name


#===================Educatuion=============
class Education(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="educations",
    )

    degree = models.CharField(max_length=200)

    institution = models.CharField(max_length=255)

    start_year = models.PositiveIntegerField()

    end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    grade = models.CharField(
        max_length=50,
        blank=True,
    )

    description = models.TextField(blank=True)

    def __str__(self):
        return self.degree
    
#=============================Experience===========
class Experience(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="experiences",
    )

    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    employment_type = models.CharField(
        max_length=100,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    currently_working = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.position} - {self.company}"

#=============Certification==========
class Certification(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )

    title = models.CharField(max_length=255)

    organization = models.CharField(max_length=255)

    issue_date = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    credential_id = models.CharField(
        max_length=255,
        blank=True,
    )

    credential_url = models.URLField(
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.title

# ===================== Portfolio =====================

class Portfolio(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="portfolios",
    )

    title = models.CharField(max_length=255)

    project_type = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(blank=True)

    project_url = models.URLField(blank=True)

    github_url = models.URLField(blank=True)

    image = models.ImageField(
        upload_to="portfolio/",
        blank=True,
        null=True,
    )

    technologies = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: React, Django, PostgreSQL",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#==============Notication===============
class NotificationSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )

    email = models.BooleanField(default=True)
    jobs = models.BooleanField(default=True)
    applications = models.BooleanField(default=True)
    marketing = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Notification Settings"