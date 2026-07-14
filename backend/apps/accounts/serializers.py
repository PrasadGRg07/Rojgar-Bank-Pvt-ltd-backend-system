import re

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def normalize_username(value: str) -> str:
    if not value:
        return ""
    value = re.sub(r"[^A-Za-z0-9@./+\-_]", "", value)
    return value.strip()

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    office_phone = serializers.SerializerMethodField()
    official_email = serializers.SerializerMethodField()
    linkedin_id = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    company_size = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    contact_person = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "name", "email", "first_name", "last_name", "role", "employee_id", "company_name",
            "address", "office_phone", "official_email", "linkedin_id", "industry", "company_size", "website",
            "facebook", "contact_person", "mobile", "intro"
        )

    def get_name(self, obj):
        full_name = obj.get_full_name()
        if full_name:
            return full_name
        if getattr(obj, "username", None):
            return obj.username
        return obj.email

    def _get_profile_field(self, obj, field_name, default=""):
        profile = getattr(obj, "employee_profile", None)
        if profile:
            return getattr(profile, field_name, default) or default
        return default

    def get_company_name(self, obj):
        # Prefer company stored on EmployeeProfile, fallback to user.company
        profile = getattr(obj, "employee_profile", None)
        if profile and getattr(profile, "company_name", None):
            return profile.company_name
        return getattr(obj, "company", None) or ""

    def get_address(self, obj):
        return self._get_profile_field(obj, "address")

    def get_office_phone(self, obj):
        return self._get_profile_field(obj, "office_phone")

    def get_official_email(self, obj):
        return self._get_profile_field(obj, "official_email", default=obj.email)

    def get_linkedin_id(self, obj):
        return self._get_profile_field(obj, "linkedin_id")

    def get_industry(self, obj):
        return self._get_profile_field(obj, "industry", default="Automobile")

    def get_company_size(self, obj):
        return self._get_profile_field(obj, "company_size")

    def get_website(self, obj):
        return self._get_profile_field(obj, "website")

    def get_facebook(self, obj):
        return self._get_profile_field(obj, "facebook")

    def get_contact_person(self, obj):
        return self._get_profile_field(obj, "contact_person", default=obj.get_full_name() or obj.username)

    def get_mobile(self, obj):
        return self._get_profile_field(obj, "mobile", default=self._get_profile_field(obj, "phone_number"))

    def get_intro(self, obj):
        return self._get_profile_field(obj, "intro")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "role",
            "employee_id",
            "company_name",
            "phone_number",
        )
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        username = normalize_username(attrs.get("username") or "")
        if username:
            attrs["username"] = username
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        company_name = validated_data.pop("company_name", None)
        phone_number = validated_data.pop("phone_number", None)
        password = validated_data.pop("password")

        username = normalize_username(validated_data.get("username") or "")
        if not username:
            username = normalize_username(validated_data.get("email") or "")
        validated_data["username"] = username

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        profile_defaults = {}

        if company_name:
            profile_defaults["company_name"] = company_name

        if phone_number:
            profile_defaults["phone_number"] = phone_number

        if user.role == User.Role.EMPLOYEE:
            try:
                from apps.employee.models import EmployeeProfile

                EmployeeProfile.objects.update_or_create(
                    user=user,
                    defaults=profile_defaults,
                )
            except Exception:
                if company_name:
                    user.company = company_name
                    user.save()

        elif user.role == User.Role.JOBSEEKER:
            try:
                from apps.jobseeker.models import JobSeekerProfile

                JobSeekerProfile.objects.get_or_create(user=user)
            except Exception as e:
                print(e)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].required = False
        self.fields["username"].allow_blank = True
        self.fields["email"].required = False
        self.fields["email"].allow_blank = True

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def _get_user_from_credentials(self, username_or_email, password):
        user = User.objects.filter(Q(email__iexact=username_or_email) | Q(username=username_or_email)).first()
        if user and user.check_password(password):
            return user
        return None

    def validate(self, attrs):
        username_or_email = attrs.get("username") or attrs.get("email")
        password = attrs.get("password")

        if not username_or_email or not password:
            raise AuthenticationFailed("Invalid username or password")

        user = self._get_user_from_credentials(username_or_email, password)
        if user is None:
            raise AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        self.user = user
        refresh = self.get_token(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        data["user"] = UserSerializer(user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value