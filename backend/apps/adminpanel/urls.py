from django.urls import path
from .views import( AdminLoginView, 
                   UserListCreateView, UserDetailView, 
                   PendingJobListView, ApprovedJobListView, AdminJobDetailView, RejectedJobListView, ApproveJobView, RejectJobView,
                   EmployeeListView,
                   AdminSubscriptionListView, AdminForwardSubscriptionView, AdminRejectSubscriptionView, AdminDashboardStatsView, )

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("jobs/pending/", PendingJobListView.as_view(), name="pending-jobs"),
    path("jobs/approved/", ApprovedJobListView.as_view(), name="approved-jobs"),
    path("jobs/<int:pk>/", AdminJobDetailView.as_view(), name="admin-job-detail"),
    path("jobs/rejected/", RejectedJobListView.as_view(), name="rejected-jobs"),
    path("jobs/<int:pk>/approve/", ApproveJobView.as_view(), name="approve-job"),
    path("jobs/<int:pk>/reject/", RejectJobView.as_view(), name="reject-job"),
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("subscriptions/", AdminSubscriptionListView.as_view(), name="admin-subscription-list"),
    path("subscriptions/<int:pk>/forward/", AdminForwardSubscriptionView.as_view(), name="admin-forward-subscription"),
    path("subscriptions/<int:pk>/reject/", AdminRejectSubscriptionView.as_view(), name="admin-reject-subscription"),
    path("dashboard/stats/", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),
]