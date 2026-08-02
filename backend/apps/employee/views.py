from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeProfile, Job
from apps.jobseeker.models import JobApplication
from .serializers import ( JobSerializer, EmployeeJobApplicationSerializer, )
from django.shortcuts import get_object_or_404
class EmployeeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'employee':
            return Response({'detail': 'Forbidden'}, status=403)

        profile = getattr(request.user, 'employee_profile', None)
        total_jobs = Job.objects.filter(user=request.user).count()
        active_jobs = Job.objects.filter(user=request.user, status='approved').count()
        total_applicants = JobApplication.objects.filter(job__user=request.user).count()
        shortlisted_applicants = JobApplication.objects.filter(job__user=request.user, status='shortlisted').count()

        recent_applications_qs = JobApplication.objects.filter(job__user=request.user).order_by('-applied_at')[:5]
        recent_applications = []
        for app in recent_applications_qs:
            recent_applications.append({
                'id': app.id,
                'name': app.applicant.get_full_name() or app.applicant.username,
                'position': app.job.title,
                'date': app.applied_at.strftime('%Y-%m-%d'),
                'status': app.status.capitalize(),
            })

        return Response({
            'message': f'Welcome {request.user.get_full_name() or request.user.username}',
            'role': request.user.role,
            'department': profile.department if profile else None,
            'designation': profile.designation if profile else None,
            'company_name': profile.company_name if profile else getattr(request.user, 'company', None),
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applicants': total_applicants,
            'shortlisted_applicants': shortlisted_applicants,
            'recent_applications': recent_applications,
        })


class JobListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
            serializer.save(
                user=self.request.user,
                status="draft"
            )

class SubmitJobForReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        job = get_object_or_404(
            Job,
            pk=pk,
            user=request.user
        )

        if job.status != "draft":
            return Response(
                {"message": "Only draft jobs can be submitted."},
                status=400,
            )

        job.status = "pending"
        job.save()

        return Response({
            "message": "Job submitted for admin review."
        })
class JobDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)
    
class ApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            pk=job_id,
            user=request.user,
        )

        applications = JobApplication.objects.filter(
            job=job
        ).order_by("-applied_at")

        serializer = EmployeeJobApplicationSerializer(
            applications,
            many=True,
        )

        return Response(serializer.data)
    
class ApplicantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        application = get_object_or_404(
            JobApplication,
            pk=pk,
            job__user=request.user,
        )

        serializer = EmployeeJobApplicationSerializer(
            application
        )

        return Response(serializer.data)
    
class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        application = get_object_or_404(
            JobApplication,
            pk=pk,
            job__user=request.user,
        )

        status_value = request.data.get("status")

        allowed = [
            "pending",
            "reviewing",
            "shortlisted",
            "rejected",
            "hired",
        ]

        if status_value not in allowed:
            return Response(
                {
                    "message": "Invalid status."
                },
                status=400,
            )

        application.status = status_value
        application.save()

        serializer = EmployeeJobApplicationSerializer(
            application
        )

        return Response(serializer.data)