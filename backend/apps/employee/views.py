from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeProfile, Job
from .serializers import JobSerializer

class EmployeeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'employee':
            return Response({'detail': 'Forbidden'}, status=403)

        profile = getattr(request.user, 'employee_profile', None)
        total_jobs = Job.objects.filter(user=request.user).count()

        return Response({
            'message': f'Welcome {request.user.get_full_name() or request.user.username}',
            'role': request.user.role,
            'department': profile.department if profile else None,
            'designation': profile.designation if profile else None,
            'company_name': profile.company_name if profile else getattr(request.user, 'company', None),
            'total_jobs': total_jobs,
            'active_jobs': total_jobs,
            'total_applicants': 0,
            'shortlisted_applicants': 0,
        })


class JobListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)