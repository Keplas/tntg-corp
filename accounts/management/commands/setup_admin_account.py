"""
Management command: setup_admin_account
Ensures there is exactly one clean monitoring-only admin account.

- Sets user_role='admin', market_type='none', is_superuser=True
- Strips marketplace participation (no cart, no loyalty earning)
- Idempotent: safe to run multiple times

Usage:
    python manage.py setup_admin_account
    python manage.py setup_admin_account --username Director --email admin@tntg-corp.com
"""

from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = "Configure the platform administrator account (monitoring-only, no marketplace)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", default="Director",
            help="Username of the admin account to configure (default: Director)",
        )
        parser.add_argument(
            "--email", default=None,
            help="Update the admin's email address (optional)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        new_email = options.get("email")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No user with username '{username}' found."))
            self.stderr.write("Available superusers:")
            for u in CustomUser.objects.filter(is_superuser=True):
                self.stderr.write(f"  {u.username} ({u.email})")
            return

        changed = []

        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            changed.append("is_superuser=True, is_staff=True")

        if user.user_role != "admin":
            user.user_role = "admin"
            changed.append("user_role='admin'")

        if user.market_type != "none":
            user.market_type = "none"
            changed.append("market_type='none'")

        if new_email and user.email != new_email:
            user.email = new_email
            changed.append(f"email='{new_email}'")

        if changed:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated '{username}': {', '.join(changed)}"
                )
            )
        else:
            self.stdout.write(f"'{username}' is already correctly configured as platform admin.")

        self.stdout.write("")
        self.stdout.write(f"  Username   : {user.username}")
        self.stdout.write(f"  Email      : {user.email}")
        self.stdout.write(f"  Role       : {user.user_role}")
        self.stdout.write(f"  Market type: {user.market_type}")
        self.stdout.write(f"  Superuser  : {user.is_superuser}")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "REMINDER: Remove any non-admin emails from this account in Django admin "
                "→ Accounts → Email addresses."
            )
        )
