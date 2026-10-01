from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = (
            "id",
            "full_name",
            "email",
            "phone_number",
            "subject",
            "message",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at")


class ContactMessageAdminSerializer(ContactMessageSerializer):
    """Used by the admin detail endpoint so a message's status can be updated."""

    class Meta(ContactMessageSerializer.Meta):
        read_only_fields = ("created_at",)
