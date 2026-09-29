from rest_framework import generics, parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.permissions import IsAdminOrSuperAdmin
from .models import (
    AboutAchievement,
    AboutLeader,
    AboutPage,
    AboutPillar,
    AboutTeamMember,
)
from .serializers import (
    AboutAchievementSerializer,
    AboutLeaderSerializer,
    AboutPageSerializer,
    AboutPillarSerializer,
    AboutTeamMemberSerializer,
)

# Collections that make up the About page, in the order the public page renders them.
COLLECTIONS = (
    ("achievements", AboutAchievement, AboutAchievementSerializer),
    ("leadership", AboutLeader, AboutLeaderSerializer),
    ("pillars", AboutPillar, AboutPillarSerializer),
    ("team", AboutTeamMember, AboutTeamMemberSerializer),
)


def is_admin(user):
    return bool(user and user.is_authenticated and user.role in ("admin", "superadmin"))


def serialize_about(request, include_hidden):
    """Build the whole About page payload, optionally including hidden items."""
    context = {"request": request}

    payload = {
        "page": AboutPageSerializer(AboutPage.get_solo(), context=context).data,
    }

    for key, model, serializer_class in COLLECTIONS:
        queryset = model.objects.all()
        if not include_hidden:
            queryset = queryset.filter(is_active=True)
        payload[key] = serializer_class(queryset, many=True, context=context).data

    return payload


class PublicAboutView(APIView):
    """Everything the public /about page needs, in a single unauthenticated call."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(serialize_about(request, include_hidden=False))


class ManageAboutView(APIView):
    """Admin read/write access to the About page copy, including hidden items."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        return Response(serialize_about(request, include_hidden=True))

    def patch(self, request):
        return self._save(request)

    def put(self, request):
        return self._save(request)

    def _save(self, request):
        page = AboutPage.get_solo()
        serializer = AboutPageSerializer(page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AboutItemMixin:
    """Public reads, admin-only writes.

    Mirrors ``apps.blog.views``: GET skips JWT authentication so a stale token in
    localStorage can never turn a public page into a 401.
    """

    parser_classes = [
        parsers.JSONParser,
        parsers.FormParser,
        parsers.MultiPartParser,
    ]

    def get_authenticators(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return [JWTAuthentication()]
        return []

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        queryset = self.model_class.objects.all()
        if is_admin(self.request.user):
            return queryset
        return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class AboutItemListCreateView(AboutItemMixin, generics.ListCreateAPIView):
    pass


class AboutItemDetailView(AboutItemMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class AboutAchievementListCreateView(AboutItemListCreateView):
    model_class = AboutAchievement
    serializer_class = AboutAchievementSerializer


class AboutAchievementDetailView(AboutItemDetailView):
    model_class = AboutAchievement
    serializer_class = AboutAchievementSerializer


class AboutLeaderListCreateView(AboutItemListCreateView):
    model_class = AboutLeader
    serializer_class = AboutLeaderSerializer


class AboutLeaderDetailView(AboutItemDetailView):
    model_class = AboutLeader
    serializer_class = AboutLeaderSerializer


class AboutPillarListCreateView(AboutItemListCreateView):
    model_class = AboutPillar
    serializer_class = AboutPillarSerializer


class AboutPillarDetailView(AboutItemDetailView):
    model_class = AboutPillar
    serializer_class = AboutPillarSerializer


class AboutTeamMemberListCreateView(AboutItemListCreateView):
    model_class = AboutTeamMember
    serializer_class = AboutTeamMemberSerializer


class AboutTeamMemberDetailView(AboutItemDetailView):
    model_class = AboutTeamMember
    serializer_class = AboutTeamMemberSerializer
