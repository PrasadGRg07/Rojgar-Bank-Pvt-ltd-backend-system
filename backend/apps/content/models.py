from django.conf import settings
from django.db import models


class AboutPage(models.Model):
    """Singleton row holding the narrative copy of the public About page."""

    SINGLETON_PK = 1

    # Hero
    hero_title = models.CharField(max_length=255, blank=True)
    hero_title_highlight = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)

    # Company introduction
    intro_paragraphs = models.TextField(
        blank=True,
        help_text="Rich text. Wrap each paragraph in its own <p> tag.",
    )
    show_intro = models.BooleanField(default=True)
    commitment_title = models.CharField(max_length=255, blank=True)
    commitment_text = models.TextField(blank=True)
    show_commitment = models.BooleanField(default=True)

    # Achievements
    show_achievements = models.BooleanField(default=True)
    achievements_title = models.CharField(max_length=255, blank=True)
    achievements_paragraphs = models.TextField(
        blank=True,
        help_text="Rich text shown under the achievement stats.",
    )

    # Leadership
    show_leadership = models.BooleanField(default=True)
    leadership_title = models.CharField(max_length=255, blank=True)
    leadership_subtitle = models.TextField(blank=True)

    # Mission / Vision / Why us pillars
    show_pillars = models.BooleanField(default=True)
    pillars_title = models.CharField(max_length=255, blank=True)

    # Team
    show_team = models.BooleanField(default=True)
    team_title = models.CharField(max_length=255, blank=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="about_page_updates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About page"
        verbose_name_plural = "About page"

    def __str__(self):
        return "About page"

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_PK
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # The About page always exists, so deleting it is a no-op.
        return

    @classmethod
    def get_solo(cls):
        page, _ = cls.objects.get_or_create(pk=cls.SINGLETON_PK)
        return page


class AboutListItem(models.Model):
    """Shared ordering / visibility behaviour for About page collections."""

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ("order", "id")

    def save(self, *args, **kwargs):
        # Only auto-assign a position for brand new rows, never on updates.
        if self._state.adding and not self.order:
            highest = type(self).objects.aggregate(models.Max("order"))["order__max"]
            self.order = (highest or 0) + 1
        super().save(*args, **kwargs)


class AboutAchievement(AboutListItem):
    """A single stat card, e.g. "50,000+ / Qualified Candidate CV Database"."""

    value = models.CharField(max_length=50)
    label = models.CharField(max_length=255)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return f"{self.value} — {self.label}"


class AboutLeader(AboutListItem):
    """A leadership portrait with a signed message."""

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, blank=True)
    message = models.TextField(blank=True)
    image = models.ImageField(upload_to="about/leadership/", blank=True, null=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Leader"
        verbose_name_plural = "Leadership"

    def __str__(self):
        return f"{self.name} — {self.role}" if self.role else self.name


class AboutPillar(AboutListItem):
    """A Mission / Vision / Opportunities / Why-us block."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="about/pillars/", blank=True, null=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Pillar"
        verbose_name_plural = "Pillars"

    def __str__(self):
        return self.title


class AboutTeamMember(AboutListItem):
    """A card in the "Our Team" grid."""

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="about/team/", blank=True, null=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Team member"
        verbose_name_plural = "Team members"

    def __str__(self):
        return f"{self.name} — {self.role}" if self.role else self.name
