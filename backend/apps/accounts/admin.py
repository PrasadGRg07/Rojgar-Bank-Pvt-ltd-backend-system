from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "company", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role",)}),
        ("Company Info", {"fields": ("company", "employee_id")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Company Info", {"fields": ("company", "employee_id")} ),
    )


admin.site.register(CustomUser, CustomUserAdmin)