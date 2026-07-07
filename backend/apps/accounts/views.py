from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, parsers
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer

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