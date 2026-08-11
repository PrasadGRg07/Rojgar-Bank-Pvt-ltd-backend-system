from rest_framework import serializers
from .models import TrainingSession, TrainingEnrollment


class TrainingSessionSerializer(serializers.ModelSerializer):
    # See BlogArticleSerializer.is_published for why this is declared explicitly.
    is_active = serializers.BooleanField(default=True, required=False)
    image = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = (
            "id",
            "title",
            "image",
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

    def get_image(self, obj):
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
