from django.urls import path
from .views import (
    SuperAdminLoginView,
    SuperAdminSubscriptionListView,
    SuperAdminActivateSubscriptionView,
    SuperAdminRejectSubscriptionView,
    SuperAdminUpdateSubscriptionView,
)

urlpatterns = [
    path("login/", SuperAdminLoginView.as_view()),
    path("subscriptions/", SuperAdminSubscriptionListView.as_view(), name="superadmin-subscription-list"),
    path("subscriptions/<int:pk>/activate/", SuperAdminActivateSubscriptionView.as_view(), name="superadmin-activate-subscription"),
    path("subscriptions/<int:pk>/reject/", SuperAdminRejectSubscriptionView.as_view(), name="superadmin-reject-subscription"),
    path("subscriptions/<int:pk>/update/", SuperAdminUpdateSubscriptionView.as_view(), name="superadmin-update-subscription"),
]