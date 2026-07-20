from django.urls import path
from .views import (
    SuperAdminLoginView,

)

urlpatterns = [
    path("login/", SuperAdminLoginView.as_view()),

    
]