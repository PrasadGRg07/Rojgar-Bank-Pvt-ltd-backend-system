from rest_framework import serializers
from .models import (
    JobSeekerProfile,
    Skill,
    Education,
    Experience,
    Certification,
    Portfolio,
    
)
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "level",
        ]
        read_only_fields = ["id"]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"
        read_only_fields = ["id", "profile"]

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "id",
            "degree",
            "institution",
            "start_year",
            "end_year",
            "grade",
            "description",
        ]
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"
        read_only_fields = ["id", "profile"]
        
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = [
            "id",
            "title",
            "organization",
            "issue_date",
            "expiry_date",
            "credential_id",
            "credential_url",
            "description",
        ]
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"
        read_only_fields = ["id", "profile"]


class ExperienceSerializer(serializers.ModelSerializer):
    end_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Experience
        fields = "__all__"
        read_only_fields = ["id", "profile"]

        

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            "id",
            "title",
            "project_type",
            "description",
            "project_url",
            "github_url",
            "image",
            "technologies",
            "created_at",

        ]
        read_only_fields = ["id", "created_at"]


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
    )

    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
    )

    email = serializers.EmailField(
        source="user.email",
        required=False,
    )

    skills = SkillSerializer(
        many=True,
        read_only=True,
    )

    educations = EducationSerializer(
        many=True,
        read_only=True,
    )

    experiences = ExperienceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "profile_picture",
            "resume",
            "bio",
            "portfolio",
            "linkedin",
            "github",
            "skills",
            "educations",
            "experiences",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]

        if "last_name" in user_data:
            user.last_name = user_data["last_name"]

        if "email" in user_data:
            user.email = user_data["email"]

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
#====== Resume ==========
class ResumeSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    uploaded_at = serializers.DateTimeField(
        source="updated_at",
        read_only=True,
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            "resume",
            "file_name",
            "file_url",
            "uploaded_at",
        ]

    def get_file_name(self, obj):
        if obj.resume:
            return obj.resume.name.split("/")[-1]
        return None

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.resume:
            return request.build_absolute_uri(obj.resume.url)

        return None
    
   #===========Acount Settings ========
class AccountSettingsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
    )

    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
    )

    email = serializers.EmailField(
        source="user.email",
        required=False,
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]

        if "last_name" in user_data:
            user.last_name = user_data["last_name"]

        if "email" in user_data:
            user.email = user_data["email"]

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance