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
from apps.employee.models import Job, EmployeeProfile, Subscription
from apps.employee.serializers import JobSerializer
from apps.jobseeker.models import JobApplication
from rest_framework import serializers as drf_serializers

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
    
  

class EmployeeListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employees = User.objects.filter(role="employee").order_by("-date_joined")
        data = []
        for u in employees:
            profile = None
            try:
                profile = u.employee_profile
            except Exception:
                pass
            data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "company": getattr(u, "company", "") or (profile.company_name if profile else ""),
                "phone": getattr(u, "phone", ""),
                "is_active": u.is_active,
                "date_joined": u.date_joined.strftime("%Y-%m-%d"),
                "job_count": Job.objects.filter(user=u).count(),
            })
        return Response(data)

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


class AdminSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        subs = Subscription.objects.select_related('user').all()
        data = []
        for s in subs:
            # Auto-expire check
            s.check_and_expire()
            slip_url = None
            if s.payment_slip:
                try:
                    slip_url = request.build_absolute_uri(s.payment_slip.url)
                except Exception:
                    pass
            days_remaining = None
            if s.expires_at and s.status == 'active':
                delta = s.expires_at - timezone.now()
                days_remaining = max(0, delta.days)
            data.append({
                'id': s.id,
                'employee': s.user.username,
                'email': s.user.email,
                'plan': s.plan,
                'amount': str(s.amount),
                'status': s.status,
                'status_display': s.get_status_display(),
                'payment_slip': slip_url,
                'admin_note': s.admin_note,
                'rejection_reason': s.rejection_reason,
                'expires_at': s.expires_at.strftime('%Y-%m-%d') if s.expires_at else None,
                'days_remaining': days_remaining,
                'created_at': s.created_at.strftime('%Y-%m-%d'),
            })
        return Response(data)


class AdminForwardSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        note = request.data.get('admin_note', '')
        sub.status = 'forwarded'
        sub.admin_note = note
        sub.reviewed_by = request.user
        sub.save()
        return Response({'message': 'Forwarded to superadmin.', 'status': sub.status})


class AdminRejectSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != "admin":
            return Response({"error": "Unauthorized"}, status=403)
        subscription = get_object_or_404(Subscription, pk=pk)
        
        rejection_reason = request.data.get("rejection_reason")
        
        subscription.status = "rejected"
        if rejection_reason:
            subscription.rejection_reason = rejection_reason
            
        subscription.save()
        return Response({"message": "Subscription rejected."})

class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "admin":
            return Response({"error": "Unauthorized"}, status=403)
        
        total_users = User.objects.filter(role="jobseeker").count()
        employers = User.objects.filter(role="employee").count()
        active_jobs = Job.objects.filter(status="approved").count()
        applications = JobApplication.objects.count()

        return Response({
            "total_users": total_users,
            "employers": employers,
            "active_jobs": active_jobs,
            "applications": applications
        })