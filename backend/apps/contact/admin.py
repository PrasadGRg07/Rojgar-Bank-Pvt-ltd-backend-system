from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone_number", "subject", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "phone_number", "subject", "message")
    list_editable = ("status",)
