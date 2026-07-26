from django.urls import path
from .views import ( EmployeeDashboardView, 
                    JobListCreateView, SubmitJobForReviewView, JobDetailView,  
                    ApplicantsView, ApplicantDetailView, UpdateApplicationStatusView,)

urlpatterns = [
    path('dashboard/', EmployeeDashboardView.as_view()),
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/submit/', SubmitJobForReviewView.as_view(), name="submit-job-review", ),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail", ),
    path( "jobs/<int:job_id>/applications/", ApplicantsView.as_view(), name="job-applicants", ),
    path( "applications/<int:pk>/", ApplicantDetailView.as_view(), name="application-detail", ),
    path("applications/<int:pk>/status/", UpdateApplicationStatusView.as_view(), name="application-status", ),
    
]