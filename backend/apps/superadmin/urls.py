from django.urls import path
from .views import (
    SuperAdminLoginView,
    SuperAdminSubscriptionListView,
    SuperAdminActivateSubscriptionView,
    SuperAdminRejectSubscriptionView,
    SuperAdminUpdateSubscriptionView,
    SuperAdminUserListView,
    SuperAdminGrantSpecialAccountView,
    SuperAdminRevokeSpecialAccountView,
    SuperAdminRoleStatsView
)

urlpatterns = [
    path("login/", SuperAdminLoginView.as_view()),
    path("subscriptions/", SuperAdminSubscriptionListView.as_view(), name="superadmin-subscription-list"),
    path("subscriptions/<int:pk>/activate/", SuperAdminActivateSubscriptionView.as_view(), name="superadmin-activate-subscription"),
    path("subscriptions/<int:pk>/reject/", SuperAdminRejectSubscriptionView.as_view(), name="superadmin-reject-subscription"),
    path("subscriptions/<int:pk>/update/", SuperAdminUpdateSubscriptionView.as_view(), name="superadmin-update-subscription"),
    path("users/", SuperAdminUserListView.as_view(), name="superadmin-user-list"),
    path("users/<int:pk>/grant-special/", SuperAdminGrantSpecialAccountView.as_view(), name="superadmin-grant-special"),
    path("users/<int:pk>/revoke-special/", SuperAdminRevokeSpecialAccountView.as_view(), name="superadmin-revoke-special"),
    path("roles/stats/", SuperAdminRoleStatsView.as_view(), name="superadmin-role-stats"),
]