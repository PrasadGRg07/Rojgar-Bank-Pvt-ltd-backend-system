from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, 
    RegisterView,
    ChangePasswordView,
    UpdateProfileView,
    UpdateEmailView,
    SendOTPView,
    MeView
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("update-profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("update-email/", UpdateEmailView.as_view(), name="update_email"),
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("me/", MeView.as_view(), name="me"),
]