from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    mainCategory = serializers.CharField(source='main_category', required=False, allow_blank=True)
    subCategory = serializers.CharField(source='sub_category', required=False, allow_blank=True)
    postingDate = serializers.CharField(source='posting_date', required=False, allow_blank=True)
    postingPeriod = serializers.CharField(source='posting_period', required=False, allow_blank=True)
    jobLevel = serializers.CharField(source='job_level', required=False, allow_blank=True)
    specificLocation = serializers.CharField(source='specific_location', required=False, allow_blank=True)
    workingTime = serializers.CharField(source='working_time', required=False, allow_blank=True)
    salaryPeriod = serializers.CharField(source='salary_period', required=False, allow_blank=True)
    salaryRange = serializers.CharField(source='salary_range', required=False, allow_blank=True)
    postToATS = serializers.BooleanField(source='post_to_ats', required=False, default=False)

    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "experience",
            "education",
            "skills",
            "description",
            "mainCategory",
            "subCategory",
            "openings",
            "postingDate",
            "postingPeriod",
            "jobLevel",
            "district",
            "municipality",
            "specificLocation",
            "workingTime",
            "currency",
            "salaryPeriod",
            "salaryRange",
            "gender",
            "license",
            "vehicle",
            "postToATS",
            "created_at",
        )
