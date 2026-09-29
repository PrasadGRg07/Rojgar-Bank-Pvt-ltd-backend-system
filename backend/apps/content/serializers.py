from rest_framework import serializers

from .models import (
    AboutAchievement,
    AboutLeader,
    AboutPage,
    AboutPillar,
    AboutTeamMember,
)


class ImageURLMixin:
    """Adds a read-only ``image_url`` field holding an absolute media URL.

    ``image_url`` stays absolute in both environments: Cloudinary already
    returns absolute URLs, and local development gets them rebuilt from the
    current request so the React app can load them directly.
    """

    def get_image_url(self, obj):
        if not obj.image:
            return None

        url = obj.image.url
        if url.startswith("http"):
            return url

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)
        return url

    def create(self, validated_data):
        # remove_image only affects updates, never creation.
        validated_data.pop("remove_image", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Images arrive as multipart uploads, so an absent file means "keep the
        # current one". Clearing one is an explicit request via remove_image.
        if validated_data.pop("remove_image", False):
            validated_data["image"] = None
        return super().update(instance, validated_data)


class AboutAchievementSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = AboutAchievement
        fields = ("id", "value", "label", "order", "is_active")
        read_only_fields = ("id",)


class AboutLeaderSerializer(ImageURLMixin, serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = AboutLeader
        fields = (
            "id",
            "name",
            "role",
            "message",
            "image",
            "image_url",
            "remove_image",
            "order",
            "is_active",
        )
        read_only_fields = ("id",)


class AboutPillarSerializer(ImageURLMixin, serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = AboutPillar
        fields = (
            "id",
            "title",
            "description",
            "image",
            "image_url",
            "remove_image",
            "order",
            "is_active",
        )
        read_only_fields = ("id",)


class AboutTeamMemberSerializer(ImageURLMixin, serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = AboutTeamMember
        fields = (
            "id",
            "name",
            "role",
            "bio",
            "image",
            "image_url",
            "remove_image",
            "order",
            "is_active",
        )
        read_only_fields = ("id",)


class AboutPageSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = (
            "hero_title",
            "hero_title_highlight",
            "hero_subtitle",
            "intro_paragraphs",
            "show_intro",
            "commitment_title",
            "commitment_text",
            "show_commitment",
            "show_achievements",
            "achievements_title",
            "achievements_paragraphs",
            "show_leadership",
            "leadership_title",
            "leadership_subtitle",
            "show_pillars",
            "pillars_title",
            "show_team",
            "team_title",
            "updated_by_name",
            "updated_at",
        )
        read_only_fields = ("updated_by_name", "updated_at")

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return None
        return obj.updated_by.get_full_name() or obj.updated_by.username
