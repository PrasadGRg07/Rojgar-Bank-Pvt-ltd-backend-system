from django.db import models
from apps.accounts.models import CustomUser

class Conversation(models.Model):
    participant_1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="conversations_started")
    participant_2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="conversations_received")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant_1', 'participant_2')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.participant_1.username} - {self.participant_2.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender.username} at {self.created_at}"
