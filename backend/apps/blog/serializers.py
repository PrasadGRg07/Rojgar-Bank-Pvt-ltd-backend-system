from rest_framework import serializers
from .models import BlogArticle


class BlogArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    # Declared explicitly (rather than left to ModelSerializer auto-generation):
    # DRF's BooleanField treats a key missing from multipart/form-data (used
    # when uploading cover_image) as an explicit False instead of falling
    # back to the model default, so the default must be set here too.
    is_published = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = BlogArticle
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "cover_image",
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
