from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationListSerializer, MessageSerializer
from apps.accounts.models import CustomUser

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(participant_1=user) | Q(participant_2=user))

class StartConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        other_participant_id = request.data.get('participant_id')
        if not other_participant_id:
            return Response({"error": "participant_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if int(other_participant_id) == request.user.id:
            return Response({"error": "Cannot start conversation with yourself"}, status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(CustomUser, id=other_participant_id)

        # Check if conversation already exists
        conversation = Conversation.objects.filter(
            (Q(participant_1=request.user) & Q(participant_2=other_user)) |
            (Q(participant_1=other_user) & Q(participant_2=request.user))
        ).first()

        if not conversation:
            conversation = Conversation.objects.create(
                participant_1=request.user,
                participant_2=other_user
            )

        serializer = ConversationListSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        user = self.request.user
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check permissions
        if conversation.participant_1 != user and conversation.participant_2 != user:
            return Message.objects.none()

        return conversation.messages.all()

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        user = self.request.user
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check permissions
        if conversation.participant_1 != user and conversation.participant_2 != user:
            return # Should raise PermissionDenied

        serializer.save(sender=user, conversation=conversation)
        
        # Update conversation updated_at
        conversation.save()

class MarkMessagesReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        user = request.user
        
        if conversation.participant_1 != user and conversation.participant_2 != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
        unread_messages = conversation.messages.exclude(sender=user).filter(is_read=False)
        updated_count = unread_messages.update(is_read=True)
        
        return Response({"status": "success", "messages_read": updated_count})
