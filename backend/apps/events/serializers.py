from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)
    # Write field — accepts uploaded file on POST/PUT
    image = serializers.ImageField(required=False, allow_null=True, write_only=False)
    # Read field — returns a full absolute URL
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'date', 'location', 'image', 'image_url', 'is_active', 'created_at')
        read_only_fields = ('created_at',)

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
