import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates a superuser from environment variables if one does not already exist."

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser creation: DJANGO_SUPERUSER_EMAIL or "
                    "DJANGO_SUPERUSER_PASSWORD environment variable not set."
                )
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Superuser with email '{email}' already exists. Skipping.")
            )
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{email}' created successfully!")
        )
