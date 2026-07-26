from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView, ListAPIView
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import AdminUserSerializer
from django.utils import timezone
from apps.employee.models import Job
from apps.employee.serializers import JobSerializer

User = get_user_model()

class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"message": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.role not in ["admin"]:
            return Response(
                {"message": "You are not authorized to access the admin panel. Only Admin accounts can login here."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )
# User CRUD operations
class UserListCreateView(ListCreateAPIView):

    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all().order_by("-id")
    
class UserDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    
#Job Approval
class PendingJobListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(status="pending").order_by("-created_at")
    
class ApprovedJobListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(status="approved").order_by("-created_at")
    
class RejectedJobListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(status="rejected").order_by("-created_at")
    
  

class AdminJobDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    queryset = Job.objects.all()
    

class ApproveJobView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        job.status = "approved"
        job.reviewed_by = request.user
        job.reviewed_at = timezone.now()
        job.rejection_reason = ""
        job.save()

        return Response(
            {"message": "Job approved successfully."},
            status=status.HTTP_200_OK,
        )


class RejectJobView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        reason = request.data.get(
            "reason",
            "No reason provided."
        )

        job.status = "rejected"
        job.reviewed_by = request.user
        job.reviewed_at = timezone.now()
        job.rejection_reason = reason
        job.save()

        return Response(
            {"message": "Job rejected successfully."},
            status=status.HTTP_200_OK,
        )