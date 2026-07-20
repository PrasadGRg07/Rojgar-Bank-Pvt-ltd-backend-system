from rest_framework import generics, parsers
from rest_framework.permissions import AllowAny
from apps.accounts.permissions import IsAdminOrSuperAdmin
from .models import Event
from .serializers import EventSerializer


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrSuperAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ('admin', 'superadmin'):
            return Event.objects.all()
        return Event.objects.filter(is_active=True)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ('admin', 'superadmin'):
            return Event.objects.all()
        return Event.objects.filter(is_active=True)
