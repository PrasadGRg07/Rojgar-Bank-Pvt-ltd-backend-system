from rest_framework import serializers
from .models import BlogArticle


class BlogArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(default=True, required=False)
    # Write field — accepts uploaded file on POST/PUT
    cover_image = serializers.ImageField(required=False, allow_null=True, write_only=False)
    # Read field — returns a full absolute URL
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogArticle
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "cover_image",
            "cover_image_url",
            "author_name",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("slug", "created_at", "updated_at")

    def get_author_name(self, obj):
        if not obj.author:
            return None
        return obj.author.get_full_name() or obj.author.username

    def get_cover_image_url(self, obj):
        if not obj.cover_image:
            return None
        url = obj.cover_image.url
        # Cloudinary returns absolute URLs; local dev returns relative paths
        if url.startswith('http'):
            return url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(url)
        return url
