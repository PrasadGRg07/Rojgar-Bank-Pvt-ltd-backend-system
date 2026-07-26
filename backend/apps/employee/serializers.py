from rest_framework import serializers
from .models import Job
from apps.jobseeker.models import JobApplication

class JobSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    employee_email = serializers.EmailField(
    source="user.email",
    read_only=True,
    )
    company = serializers.CharField(
    source="user.company",
    read_only=True,
)

    # Basic
    mainCategory = serializers.CharField(source="main_category", required=False, allow_blank=True)
    subCategory = serializers.CharField(source="sub_category", required=False, allow_blank=True)
    employmentType = serializers.CharField(source="employment_type", required=False, allow_blank=True)
    jobLevel = serializers.CharField(source="job_level", required=False, allow_blank=True)
    jobCode = serializers.CharField(source="job_code", required=False, allow_blank=True)

    # Description
    shortDescription = serializers.CharField(source="short_description", required=False, allow_blank=True)
    whyJoinUs = serializers.CharField(source="why_join_us", required=False, allow_blank=True)

    # Requirements
    minAge = serializers.IntegerField(source="min_age", required=False, allow_null=True)
    maxAge = serializers.IntegerField(source="max_age", required=False, allow_null=True)

    # Salary
    salaryType = serializers.CharField(source="salary_type", required=False, allow_blank=True)

    salaryMin = serializers.DecimalField(
        source="salary_min",
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    salaryMax = serializers.DecimalField(
        source="salary_max",
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    hideSalary = serializers.BooleanField(
        source="hide_salary",
        required=False,
    )

    # Location
    workMode = serializers.CharField(source="work_mode", required=False, allow_blank=True)
    mapLink = serializers.URLField(source="map_link", required=False, allow_blank=True)
    travelRequired = serializers.BooleanField(source="travel_required", required=False)

    # Benefits
    otherBenefits = serializers.CharField(source="other_benefits", required=False, allow_blank=True)

    # Application
    applicationDeadline = serializers.DateField(source="application_deadline", required=False, allow_null=True)
    joiningDate = serializers.DateField(source="joining_date", required=False, allow_null=True)
    contactEmail = serializers.EmailField(source="contact_email", required=False, allow_blank=True)
    contactPhone = serializers.CharField(source="contact_phone", required=False, allow_blank=True)
    requiredDocuments = serializers.ListField(source="required_documents", required=False)
    acceptUntilFilled = serializers.BooleanField(source="accept_until_filled", required=False)
    sendConfirmationEmail = serializers.BooleanField(source="send_confirmation_email", required=False)
    allowQuickApply = serializers.BooleanField(source="allow_quick_apply", required=False)

    # Posting
    postingDate = serializers.DateField(source="posting_date", required=False, allow_null=True)
    postingPeriod = serializers.CharField(source="posting_period", required=False, allow_blank=True)
    postToATS = serializers.BooleanField(source="post_to_ats", required=False)

    class Meta:
        model = Job

        fields = [
            "id",
            "employee_name",
            "employee_email",
            "company",

            "title",
            "mainCategory",
            "subCategory",
            "employmentType",
            "jobLevel",
            "openings",
            "workplace",
            "department",
            "jobCode",

            "shortDescription",
            "description",
            "responsibilities",
            "qualifications",
            "whyJoinUs",

            "experience",
            "education",
            "skills",
            "languages",
            "license",
            "vehicle",
            "gender",
            "minAge",
            "maxAge",

            "currency",
            "salaryType",
            "salaryMin",
            "salaryMax",
            "negotiable",
            "hideSalary",

            "province",
            "district",
            "municipality",
            "address",
            "workMode",
            "mapLink",
            "travelRequired",

            "benefits",
            "otherBenefits",

            "applicationDeadline",
            "joiningDate",
            "contactEmail",
            "contactPhone",
            "requiredDocuments",
            "acceptUntilFilled",
            "sendConfirmationEmail",
            "allowQuickApply",

            "postingDate",
            "postingPeriod",
            "postToATS",
            
             # Review

            "status",
            "reviewed_by",
            "reviewed_at",
            "rejection_reason",
            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "id",
            "employee_name",
            "employee_email",
            "company",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        
        
class EmployeeJobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(
        source="applicant.username",
        read_only=True,
    )

    applicant_email = serializers.EmailField(
        source="applicant.email",
        read_only=True,
    )

    job_title = serializers.CharField(
        source="job.title",
        read_only=True,
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job",
            "job_title",
            "applicant",
            "applicant_name",
            "applicant_email",
            "cover_letter",
            "resume",
            "status",
            "applied_at",
        ]

        read_only_fields = (
            "id",
            "job_title",
            "applicant_name",
            "applicant_email",
            "applied_at",
        )