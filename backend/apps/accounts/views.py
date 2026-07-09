from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, parsers
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer, ChangePasswordSerializer

from django.contrib.auth import get_user_model

User = get_user_model()
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = getattr(user, 'employee_profile', None)

            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            refresh['name'] = user.get_full_name() or user.username
            refresh['company_name'] = profile.company_name if profile else getattr(user, 'company', None)

            return Response({
                "message": "Registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "company_name": profile.company_name if profile else getattr(user, 'company', None),
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
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