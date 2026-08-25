from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import EmployeeProfile, Job, Subscription, SavedCandidate
from apps.jobseeker.models import JobApplication, JobSeekerProfile
from .serializers import ( JobSerializer, EmployeeJobApplicationSerializer, CandidateProfileSerializer, SavedCandidateSerializer )
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


from django.contrib.auth import get_user_model
from apps.messaging.models import Notification

class JobListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        job = serializer.save(
            user=self.request.user,
            status="draft"
        )
        
        # Optionally send a notification if they submitted immediately, but usually it's draft.
        # If we want admin to get notified on draft creation:
        User = get_user_model()
        admins = User.objects.filter(role__in=['admin', 'superadmin'])
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title=f"New Job Posted: {job.title}",
                message=f"{self.request.user.username} has posted a new job: {job.title}.",
                notification_type="job_created",
                related_job=job
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
        
        if status_value == "rejected":
            application.rejection_reason = request.data.get("rejection_reason")
        else:
            application.rejection_reason = None

        application.save()

        serializer = EmployeeJobApplicationSerializer(
            application
        )

        return Response(serializer.data)

class CandidateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateProfileSerializer

    def get_queryset(self):
        return JobSeekerProfile.objects.filter(
            user__role="jobseeker"
        ).order_by("-created_at")

class CandidateDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateProfileSerializer
    lookup_field = "user_id"

    def get_queryset(self):
        return JobSeekerProfile.objects.filter(user__role="jobseeker")


class SubscriptionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def post(self, request):
        plan = request.data.get('plan')
        amount = request.data.get('amount', 0)
        slip = request.FILES.get('payment_slip')

        if not plan:
            return Response({'detail': 'Plan is required.'}, status=400)

        sub = Subscription.objects.create(
            user=request.user,
            plan=plan,
            amount=amount,
            payment_slip=slip,
            status='pending',
        )
        return Response({'message': 'Subscription created successfully. Awaiting approval.', 'id': sub.id}, status=201)

    def get(self, request):
        from django.utils import timezone
        
        # Special accounts have unlimited access — treat as permanently subscribed
        if getattr(request.user, 'is_special_account', False):
            return Response([{
                'id': 0,
                'plan': 'special',
                'amount': '0.00',
                'status': 'active',
                'status_display': 'Active (Special Account)',
                'rejection_reason': None,
                'activated_at': request.user.date_joined.strftime('%Y-%m-%d'),
                'expires_at': None,
                'days_remaining': None,
                'created_at': request.user.date_joined.strftime('%Y-%m-%d'),
            }])
        
        subs = Subscription.objects.filter(user=request.user)
        data = []
        for s in subs:
            # Auto-expire check on every fetch
            s.check_and_expire()
            days_remaining = None
            if s.expires_at and s.status == 'active':
                delta = s.expires_at - timezone.now()
                days_remaining = max(0, delta.days)
            data.append({
                'id': s.id,
                'plan': s.plan,
                'amount': str(s.amount),
                'status': s.status,
                'status_display': s.get_status_display(),
                'rejection_reason': s.rejection_reason,
                'activated_at': s.activated_at.strftime('%Y-%m-%d') if s.activated_at else None,
                'expires_at': s.expires_at.strftime('%Y-%m-%d') if s.expires_at else None,
                'days_remaining': days_remaining,
                'created_at': s.created_at.strftime('%Y-%m-%d'),
            })
        return Response(data)

class SavedCandidateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedCandidateSerializer

    def get_queryset(self):
        return SavedCandidate.objects.filter(user=self.request.user)

class SavedCandidateToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, candidate_id):
        # Using candidate_id to fetch the JobSeekerProfile
        candidate = get_object_or_404(JobSeekerProfile, user_id=candidate_id)

        saved_candidate, created = SavedCandidate.objects.get_or_create(
            user=request.user,
            candidate=candidate
        )

        if not created:
            # If it already existed, remove it (toggle)
            saved_candidate.delete()
            return Response({"message": "Candidate removed from saved list", "is_saved": False}, status=status.HTTP_200_OK)
        return Response({"message": "Candidate saved successfully", "is_saved": True}, status=status.HTTP_201_CREATED)

class InterviewListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    from .serializers import InterviewSerializer
    serializer_class = InterviewSerializer

    def get_queryset(self):
        from .models import Interview
        return Interview.objects.filter(job__user=self.request.user).order_by('-date', '-time')

    def perform_create(self, serializer):
        interview = serializer.save(interviewer=self.request.user)
        # Create notification for candidate
        from apps.messaging.models import Notification
        Notification.objects.create(
            recipient=interview.candidate,
            title="Interview Scheduled",
            message=f"An interview has been scheduled for {interview.job.title} on {interview.date} at {interview.time}.",
            notification_type="system"
        )

class InterviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    from .serializers import InterviewSerializer
    serializer_class = InterviewSerializer

    def get_queryset(self):
        from .models import Interview
        return Interview.objects.filter(job__user=self.request.user)