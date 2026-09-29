from django.contrib import admin

from .models import (
    AboutAchievement,
    AboutLeader,
    AboutPage,
    AboutPillar,
    AboutTeamMember,
)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_title", "hero_title_highlight", "hero_subtitle")}),
        ("Introduction", {"fields": ("show_intro", "intro_paragraphs")}),
        ("Commitment", {"fields": ("show_commitment", "commitment_title", "commitment_text")}),
        ("Achievements", {"fields": ("show_achievements", "achievements_title", "achievements_paragraphs")}),
        ("Leadership", {"fields": ("show_leadership", "leadership_title", "leadership_subtitle")}),
        ("Pillars", {"fields": ("show_pillars", "pillars_title")}),
        ("Team", {"fields": ("show_team", "team_title")}),
    )
    readonly_fields = ("created_at", "updated_at", "updated_by")

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutAchievement)
class AboutAchievementAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("value", "label")
    list_editable = ("order", "is_active")


@admin.register(AboutLeader)
class AboutLeaderAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "role", "message")
    list_editable = ("order", "is_active")


@admin.register(AboutPillar)
class AboutPillarAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    list_editable = ("order", "is_active")


@admin.register(AboutTeamMember)
class AboutTeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "role", "bio")
    list_editable = ("order", "is_active")
