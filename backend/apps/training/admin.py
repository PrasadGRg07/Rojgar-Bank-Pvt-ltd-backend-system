from django.contrib import admin
from .models import TrainingSession, TrainingEnrollment


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "course_name", "start_time", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "course_name", "trainer_name")


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "training_session", "course_interest", "preferred_time", "created_at")
    search_fields = ("full_name", "email", "phone_number", "course_interest")
    list_filter = ("training_session",)
