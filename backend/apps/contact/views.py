from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.accounts.permissions import IsAdminOrSuperAdmin

from .models import ContactMessage
from .serializers import ContactMessageSerializer, ContactMessageAdminSerializer


class ContactMessageListCreateView(generics.ListCreateAPIView):
    """POST is open to the public from the "Talk to Us" page; GET (viewing the
    submitted messages) is restricted to admins."""

    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Lets an admin read, mark or delete a single message."""

    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.all()
    permission_classes = [IsAdminOrSuperAdmin]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ContactMessageAdminSerializer
        return ContactMessageSerializer
