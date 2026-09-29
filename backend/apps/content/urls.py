from django.urls import path

from .views import (
    AboutAchievementDetailView,
    AboutAchievementListCreateView,
    AboutLeaderDetailView,
    AboutLeaderListCreateView,
    AboutPillarDetailView,
    AboutPillarListCreateView,
    AboutTeamMemberDetailView,
    AboutTeamMemberListCreateView,
    ManageAboutView,
    PublicAboutView,
)

urlpatterns = [
    # Public: one call that renders the whole /about page.
    path("about/", PublicAboutView.as_view(), name="public-about"),
    # Admin: same payload including hidden items, plus About page copy editing.
    path("about/manage/", ManageAboutView.as_view(), name="manage-about"),
    path(
        "about/achievements/",
        AboutAchievementListCreateView.as_view(),
        name="about-achievement-list-create",
    ),
    path(
        "about/achievements/<int:pk>/",
        AboutAchievementDetailView.as_view(),
        name="about-achievement-detail",
    ),
    path(
        "about/leadership/",
        AboutLeaderListCreateView.as_view(),
        name="about-leader-list-create",
    ),
    path(
        "about/leadership/<int:pk>/",
        AboutLeaderDetailView.as_view(),
        name="about-leader-detail",
    ),
    path(
        "about/pillars/",
        AboutPillarListCreateView.as_view(),
        name="about-pillar-list-create",
    ),
    path(
        "about/pillars/<int:pk>/",
        AboutPillarDetailView.as_view(),
        name="about-pillar-detail",
    ),
    path(
        "about/team/",
        AboutTeamMemberListCreateView.as_view(),
        name="about-team-member-list-create",
    ),
    path(
        "about/team/<int:pk>/",
        AboutTeamMemberDetailView.as_view(),
        name="about-team-member-detail",
    ),
]
