from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'date', 'location', 'image', 'is_active', 'created_at')
        read_only_fields = ('created_at',)
