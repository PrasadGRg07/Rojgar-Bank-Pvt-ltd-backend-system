from django.urls import path
from .views import EmployeeDashboardView, JobListCreateView

urlpatterns = [
    path('dashboard/', EmployeeDashboardView.as_view()),
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
]