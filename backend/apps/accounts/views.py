from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, parsers
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer, ChangePasswordSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import random
import requests

User = get_user_model()


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, first_name=""):
    """Send OTP verification email."""
    subject = "Verify your Rojgar Bank account"
    message = f"""Hello {first_name or "there"},

Welcome to Rojgar Bank!

Your email verification code is:

    {otp}

This code will expire in 10 minutes. Do not share this code with anyone.

If you did not create an account, please ignore this email.

— The Rojgar Bank Team
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):

    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Check if email is already in CustomUser
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({"email": ["A user with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)

            pending_user = serializer.save()

            # Generate and store OTP
            otp = generate_otp()
            pending_user.otp_hash = make_password(otp)
            pending_user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)
            pending_user.otp_attempts = 0
            pending_user.save()

            try:
                send_otp_email(pending_user.email, otp, pending_user.registration_data.get('first_name'))
            except Exception as e:
                # If email fails, delete the pending user so they can try again
                pending_user.delete()
                error_message = str(e)
                if "sender not verified" in error_message.lower():
                    error_message = "Your Brevo sender email is not verified. Please verify it in the Brevo dashboard."
                elif "unauthorized" in error_message.lower():
                    error_message = "Your Brevo API key is invalid or unauthorized."
                return Response({
                    "detail": f"Failed to send OTP email: {error_message}"
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "Registered successfully. Please check your email for the OTP verification code.",
                "email": pending_user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def get(self, request):
        user = request.user
        from apps.employee.models import EmployeeProfile
        profile = getattr(user, 'employee_profile', None)

        # Build absolute URL for profile picture
        profile_picture_url = None
        if profile and profile.profile_picture:
            try:
                profile_picture_url = request.build_absolute_uri(profile.profile_picture.url)
            except Exception:
                profile_picture_url = None

        return Response({
            "username": user.username,
            "email": user.email,
            "company_name": profile.company_name if profile else (user.company or ""),
            "address": profile.address if profile else "",
            "office_phone": profile.office_phone if profile else "",
            "official_email": profile.official_email if profile else "",
            "linkedin_id": profile.linkedin_id if profile else "",
            "industry": profile.industry if profile else "",
            "company_size": profile.company_size if profile else "",
            "website": profile.website if profile else "",
            "facebook": profile.facebook if profile else "",
            "contact_person": profile.contact_person if profile else "",
            "mobile": profile.mobile if profile else "",
            "phone_number": profile.phone_number if profile else "",
            "intro": profile.intro if profile else "",
            "designation": profile.designation if profile else "",
            "department": profile.department if profile else "",
            "profile_picture": profile_picture_url,
        })

    def patch(self, request):
        user = request.user
        from apps.employee.models import EmployeeProfile
        profile, created = EmployeeProfile.objects.get_or_create(user=user)

        fields = [
            "company_name", "address", "office_phone", "official_email",
            "linkedin_id", "industry", "company_size", "website",
            "facebook", "contact_person", "mobile", "intro"
        ]

        url_fields = {"website", "facebook"}

        for field in fields:
            if field in request.data:
                value = request.data[field]
                # Auto-prefix URL fields so bare domains don't fail URLField validation
                if field in url_fields and value and not value.startswith(("http://", "https://")):
                    value = "https://" + value
                setattr(profile, field, value)

        if "company_name" in request.data:
            user.company = request.data["company_name"]
            user.save()

        # Handle profile picture upload
        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()

        # Refresh user from DB so serializer returns up-to-date profile data
        user.refresh_from_db()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class UpdateEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.email = email
        user.save()

        profile = getattr(user, 'employee_profile', None)
        if profile:
            profile.official_email = email
            profile.save()

        return Response({"detail": "Email updated successfully."}, status=status.HTTP_200_OK)


class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        from apps.employee.models import EmployeeProfile
        profile, created = EmployeeProfile.objects.get_or_create(user=user)
        profile.phone_number = phone
        profile.mobile = phone
        profile.save()

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """Verify a 6-digit OTP to activate the user's account."""

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure account isn't already created
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Lookup PendingUser
        from apps.accounts.models import PendingUser
        pending_user = PendingUser.objects.filter(email=email).first()
        
        if not pending_user:
            return Response({"detail": "No pending registration found for this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Check attempts
        if pending_user.otp_attempts >= 3:
            # Invalidate OTP after 3 failed attempts
            pending_user.otp_hash = None
            pending_user.otp_expires_at = None
            pending_user.otp_attempts = 0
            pending_user.save()
            return Response({
                "detail": "Too many failed attempts. Please request a new OTP.",
                "code": "otp_max_attempts"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check expiry
        if not pending_user.otp_expires_at or pending_user.otp_expires_at < timezone.now():
            return Response({
                "detail": "OTP has expired. Please request a new one.",
                "code": "otp_expired"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if not pending_user.otp_hash or not check_password(otp, pending_user.otp_hash):
            pending_user.otp_attempts += 1
            pending_user.save()
            remaining = 3 - pending_user.otp_attempts
            return Response({
                "detail": f"Invalid OTP. {remaining} attempt(s) remaining.",
                "code": "otp_invalid"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Success — activate account
        data = pending_user.registration_data
        
        user = User.objects.create(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', User.Role.JOBSEEKER),
            password=data.get('password'),
            is_verified=True
        )
        
        company_name = data.get('company_name')
        phone_number = data.get('phone_number')

        if user.role == User.Role.EMPLOYEE:
            try:
                from apps.employee.models import EmployeeProfile
                EmployeeProfile.objects.create(
                    user=user,
                    company_name=company_name or '',
                    phone_number=phone_number or ''
                )
            except Exception:
                if company_name:
                    user.company = company_name
                    user.save()
        elif user.role == User.Role.JOBSEEKER:
            try:
                from apps.jobseeker.models import JobSeekerProfile
                JobSeekerProfile.objects.create(user=user)
            except Exception:
                pass

        pending_user.delete()

        return Response({"detail": "Email verified successfully. You can now log in."}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """Resend OTP to the user's email."""

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.accounts.models import PendingUser
        pending_user = PendingUser.objects.filter(email=email).first()
        
        if not pending_user:
            return Response({"detail": "No pending registration found for this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate new OTP
        otp = generate_otp()
        pending_user.otp_hash = make_password(otp)
        pending_user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)
        pending_user.otp_attempts = 0
        pending_user.save()

        first_name = pending_user.registration_data.get('first_name', '')
        
        try:
            send_otp_email(pending_user.email, otp, first_name)
        except Exception as e:
            error_message = str(e)
            if "sender not verified" in error_message.lower():
                error_message = "Your Brevo sender email is not verified. Please verify it in the Brevo dashboard."
            elif "unauthorized" in error_message.lower():
                error_message = "Your Brevo API key is invalid or unauthorized."
            return Response({
                "detail": f"Failed to send OTP email: {error_message}"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    def post(self, request):
        try:
            from .serializers import GoogleLoginSerializer
            serializer = GoogleLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            credential = serializer.validated_data["credential"]

            requested_role = serializer.validated_data.get("role", User.Role.JOBSEEKER)

            # Verify token with Google
            google_response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={credential}')
            if google_response.status_code != 200:
                return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

            google_data = google_response.json()
            email = google_data.get("email")
            google_id = google_data.get("sub")
            first_name = google_data.get("given_name", "")
            last_name = google_data.get("family_name", "")

            if not email:
                return Response({"detail": "Email not provided by Google."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()

            if user:
                # User exists — link Google account if not already linked
                if not user.google_id:
                    user.google_id = google_id
                    user.auth_provider = 'google'
                    user.is_verified = True
                    user.save()
            else:
                # Create new user
                username = email.split('@')[0]
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Validate role
                if requested_role not in [User.Role.EMPLOYEE, User.Role.JOBSEEKER]:
                    requested_role = User.Role.JOBSEEKER

                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    auth_provider='google',
                    is_verified=True,
                    role=requested_role,
                )
                try:
                    if requested_role == User.Role.EMPLOYEE:
                        from apps.employee.models import EmployeeProfile
                        EmployeeProfile.objects.get_or_create(user=user)
                    else:
                        from apps.jobseeker.models import JobSeekerProfile
                        JobSeekerProfile.objects.get_or_create(user=user)
                except Exception:
                    pass

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            refresh['name'] = user.get_full_name() or user.username

            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"An error occurred during Google Login: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)