from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication APIs
    path("api/auth/", include("apps.accounts.urls")),
    path("auth/", include("apps.accounts.urls")),

    # Employee APIs
    path("api/employee/", include("apps.employee.urls")),
    path("employee/", include("apps.employee.urls")),

    # Admin APIs
    path("api/admin/", include("apps.adminpanel.urls")),
    path("adminpanel/", include("apps.adminpanel.urls")),

    # Super Admin APIs
    path("api/superadmin/", include("apps.superadmin.urls")),
    path("superadmin/", include("apps.superadmin.urls")),

    # Job Seeker APIs
    path("api/jobseeker/", include("apps.jobseeker.urls")),
    path("jobseeker/", include("apps.jobseeker.urls")),

    # Homes APIs
    path("api/blog/", include("apps.blog.urls")),
    path("blog/", include("apps.blog.urls")),

    path("api/training/", include("apps.training.urls")),
    path("training/", include("apps.training.urls")),

    path("api/events/", include("apps.events.urls")),
    path("events/", include("apps.events.urls")),

    # Messaging APIs
    path("api/messaging/", include("apps.messaging.urls")),
    path("messaging/", include("apps.messaging.urls")),
]

# Serve uploaded media files
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)