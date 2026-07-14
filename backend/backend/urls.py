from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication APIs
    path("api/auth/", include("apps.accounts.urls")),

    # Employee APIs
    path("api/employee/", include("apps.employee.urls")),
    # Admin APIs
    path("api/admin/", include("apps.adminpanel.urls")),
    # Job Seeker APIs
    path("api/jobseeker/", include("apps.jobseeker.urls")),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )