from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.accounts.permissions import IsAdminOrSuperAdmin
from .models import TrainingSession, TrainingEnrollment
from .serializers import TrainingSessionSerializer, TrainingEnrollmentSerializer


class TrainingSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = TrainingSessionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrSuperAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ("admin", "superadmin"):
            return TrainingSession.objects.all()
        return TrainingSession.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TrainingSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrainingSessionSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ("admin", "superadmin"):
            return TrainingSession.objects.all()
        return TrainingSession.objects.filter(is_active=True)


class TrainingEnrollmentListCreateView(generics.ListCreateAPIView):
    """POST is open to the public to enroll in a session; GET (viewing the
    submitted enrollments) is restricted to admins."""

    serializer_class = TrainingEnrollmentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        return TrainingEnrollment.objects.filter(training_session_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        session = generics.get_object_or_404(TrainingSession, pk=self.kwargs["pk"])
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(training_session=session, user=user)
