from rest_framework import serializers
from .models import Job, SavedCandidate, Interview
from apps.jobseeker.models import JobApplication, JobSeekerProfile, Skill, Education, Experience, Certification, Portfolio

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "level"]

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ["id", "degree", "institution", "start_year", "end_year", "grade", "description"]

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ["id", "company", "position", "employment_type", "start_date", "end_date", "currently_working", "description"]

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "title", "organization", "issue_date", "expiry_date", "credential_id", "credential_url"]

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "title", "project_type", "description", "project_url", "github_url", "image"]


class CandidateProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)
    
    class Meta:
        model = JobSeekerProfile
        fields = [
            "id", "user_id", "name", "email", "phone", "address", 
            "profile_picture", "bio", "portfolio", "linkedin", "github",
            "skills", "educations", "experiences", "certifications", "portfolios", "resume"
        ]
        
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

class JobSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    employee_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    company = serializers.SerializerMethodField()
    employer_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    employer_profile_picture = serializers.SerializerMethodField()
    employer_company_name = serializers.SerializerMethodField()

    def get_company(self, obj):
        profile = getattr(obj.user, 'employee_profile', None)
        if profile and profile.company_name:
            return profile.company_name
        return getattr(obj.user, 'company', None) or obj.user.username

    def get_employer_profile_picture(self, obj):
        request = self.context.get('request')
        profile = getattr(obj.user, 'employee_profile', None)
        if profile and profile.profile_picture:
            url = profile.profile_picture.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_employer_company_name(self, obj):
        profile = getattr(obj.user, 'employee_profile', None)
        if profile and profile.company_name:
            return profile.company_name
        return getattr(obj.user, 'company', None) or obj.user.username

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
            "employer_id",
            "employee_name",
            "employee_email",
            "company",
            "employer_profile_picture",
            "employer_company_name",

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
            "employer_id",
            "employee_name",
            "employee_email",
            "company",
            "employer_profile_picture",
            "employer_company_name",
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
            "certificates",
            "citizenship_copy",
            "rejection_reason",
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

class SavedCandidateSerializer(serializers.ModelSerializer):
    candidate = CandidateProfileSerializer(read_only=True)

    class Meta:
        model = SavedCandidate
        fields = ["id", "user", "candidate", "created_at"]
        read_only_fields = ["user", "created_at"]


class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.username", read_only=True)
    candidate_email = serializers.CharField(source="candidate.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    interviewer_name = serializers.CharField(source="interviewer.username", read_only=True)

    class Meta:
        model = Interview
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]