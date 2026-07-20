from django.urls import path
from .views import (
    TrainingSessionListCreateView,
    TrainingSessionDetailView,
    TrainingEnrollmentListCreateView,
)

urlpatterns = [
    path("sessions/", TrainingSessionListCreateView.as_view(), name="training-session-list-create"),
    path("sessions/<int:pk>/", TrainingSessionDetailView.as_view(), name="training-session-detail"),
    path(
        "sessions/<int:pk>/enroll/",
        TrainingEnrollmentListCreateView.as_view(),
        name="training-session-enroll",
    ),
]
