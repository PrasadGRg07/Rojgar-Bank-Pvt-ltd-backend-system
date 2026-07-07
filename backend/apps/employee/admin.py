from django.contrib import admin
from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "company_name", "department", "designation")
	search_fields = ("user__username", "company_name")
	raw_id_fields = ("user",)
