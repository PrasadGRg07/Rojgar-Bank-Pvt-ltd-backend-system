from rest_framework import generics, parsers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.permissions import IsAdminOrSuperAdmin
from .models import BlogArticle
from .serializers import BlogArticleSerializer


class BlogArticleListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogArticleSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def get_authenticators(self):
        # Only run JWT authentication for write operations.
        # For GET, skip strict auth so an invalid/expired token doesn't cause 401.
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return [JWTAuthentication()]
        return []

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrSuperAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ("admin", "superadmin"):
            return BlogArticle.objects.all()
        return BlogArticle.objects.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BlogArticleSerializer
    parser_classes = [
        parsers.JSONParser,
        parsers.FormParser,
        parsers.MultiPartParser,
    ]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ("admin", "superadmin"):
            return BlogArticle.objects.all()
        return BlogArticle.objects.filter(is_published=True)

    def get_object(self):
        queryset = self.get_queryset()

        if "pk" in self.kwargs:
            return generics.get_object_or_404(
                queryset,
                pk=self.kwargs["pk"],
            )

        return generics.get_object_or_404(
            queryset,
            slug=self.kwargs["slug"],
        )