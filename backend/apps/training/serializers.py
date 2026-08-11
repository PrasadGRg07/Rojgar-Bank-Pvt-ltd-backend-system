from rest_framework import serializers
from .models import TrainingSession, TrainingEnrollment


class TrainingSessionSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)
    # Write field — accepts uploaded file on POST/PUT
    image = serializers.ImageField(required=False, allow_null=True, write_only=False)
    # Read field — returns a full absolute URL
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = (
            "id",
            "title",
            "image",
            "image_url",
            "course_name",
            "description",
            "trainer_name",
            "location",
            "start_time",
            "end_time",
            "capacity",
            "is_active",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def get_image_url(self, obj):
        if not obj.image:
            return None
        url = obj.image.url
        if url.startswith('http'):
            return url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(url)
        return url


class TrainingEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingEnrollment
        fields = (
            "id",
            "training_session",
            "full_name",
            "email",
            "phone_number",
            "course_interest",
            "preferred_time",
            "created_at",
        )
        read_only_fields = ("training_session", "created_at")
