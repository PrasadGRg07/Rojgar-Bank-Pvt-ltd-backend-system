from django.urls import path
from .views import( AdminLoginView, 
                   UserListCreateView, UserDetailView, 
                   PendingJobListView, ApprovedJobListView, AdminJobDetailView, RejectedJobListView, ApproveJobView, RejectJobView, )

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("jobs/pending/", PendingJobListView.as_view(), name="pending-jobs"),
    path("jobs/approved/", ApprovedJobListView.as_view(), name="approved-jobs"),
    path("jobs/<int:pk>/", AdminJobDetailView.as_view(), name="admin-job-detail" ),
    path("jobs/rejected/", RejectedJobListView.as_view(), name="rejected-jobs"),
    path("jobs/<int:pk>/approve/", ApproveJobView.as_view(), name="approve-job"),
    path("jobs/<int:pk>/reject/", RejectJobView.as_view(), name="reject-job"),

]