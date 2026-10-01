from django.urls import path

from .views import ContactMessageListCreateView, ContactMessageDetailView

urlpatterns = [
    path("messages/", ContactMessageListCreateView.as_view(), name="contact-message-list-create"),
    path("messages/<int:pk>/", ContactMessageDetailView.as_view(), name="contact-message-detail"),
]
