from rest_framework import serializers
from .models import Conversation, Message
from apps.accounts.models import CustomUser

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'sender_role', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'conversation']

    def get_sender_name(self, obj):
        # We try to get the full name, otherwise use username
        name = f"{obj.sender.first_name} {obj.sender.last_name}".strip()
        if not name:
            if obj.sender.role == "employee":
                name = obj.sender.company or obj.sender.username
            else:
                name = obj.sender.username
        return name

class ConversationListSerializer(serializers.ModelSerializer):
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_participant', 'last_message', 'unread_count', 'updated_at']

    def get_other_participant(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        
        other_user = obj.participant_2 if obj.participant_1 == user else obj.participant_1
        
        name = f"{other_user.first_name} {other_user.last_name}".strip()
        if not name:
             if other_user.role == "employee":
                  name = other_user.company or other_user.username
             else:
                  name = other_user.username

        # Get profile picture if available depending on the role
        profile_picture = None
        if other_user.role == "employee" and hasattr(other_user, "employee_profile") and other_user.employee_profile.profile_picture:
             profile_picture = request.build_absolute_uri(other_user.employee_profile.profile_picture.url) if request else other_user.employee_profile.profile_picture.url
        elif other_user.role == "jobseeker" and hasattr(other_user, "jobseeker_profile") and other_user.jobseeker_profile.profile_picture:
             profile_picture = request.build_absolute_uri(other_user.jobseeker_profile.profile_picture.url) if request else other_user.jobseeker_profile.profile_picture.url

        return {
            'id': other_user.id,
            'name': name,
            'role': other_user.role,
            'profile_picture': profile_picture
        }

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'id': last_msg.id,
                'content': last_msg.content,
                'created_at': last_msg.created_at,
                'sender_id': last_msg.sender_id
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if not user:
            return 0
        return obj.messages.exclude(sender=user).filter(is_read=False).count()
