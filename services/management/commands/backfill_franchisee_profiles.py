"""
Management command: backfill_franchisee_profiles
Creates FranchiseeProfile records for users who have an approved
FranchiseApplication but no profile yet.

Run in Cloud Run console:
  Container → Command override: python
  Container → Args override: manage.py,backfill_franchisee_profiles

Or via gcloud:
  gcloud run jobs create backfill-profiles \
    --image REGION-docker.pkg.dev/PROJECT/REPO/IMAGE \
    --command python --args "manage.py,backfill_franchisee_profiles" \
    --region us-east1 --project tomtradecorp
  gcloud run jobs execute backfill-profiles --region us-east1
"""

from django.core.management.base import BaseCommand
from services.models import FranchiseApplication, FranchiseeProfile


class Command(BaseCommand):
    help = "Backfill FranchiseeProfile for users with approved FranchiseApplications"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be created without saving",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find approved applications that do NOT yet have a FranchiseeProfile
        approved = (
            FranchiseApplication.objects.filter(status="approved")
            .exclude(franchisee_profile__isnull=False)   # skip ones already linked to a profile
            .select_related("user")
            .order_by("created_at")  # oldest first; each user gets their earliest approved app
        )

        created = 0
        skipped = 0
        seen_users = set()  # guard against a user having 2 approved apps

        for app in approved:
            user = app.user
            if user is None:
                self.stdout.write(f"  SKIP  app#{app.pk} — no linked user")
                skipped += 1
                continue

            if user.pk in seen_users:
                self.stdout.write(
                    f"  SKIP  app#{app.pk} ({user.email}) — already processed a newer app for this user"
                )
                skipped += 1
                continue

            if hasattr(user, "franchisee_profile"):
                self.stdout.write(f"  SKIP  {user.email} — FranchiseeProfile already exists")
                seen_users.add(user.pk)
                skipped += 1
                continue

            seen_users.add(user.pk)
            self.stdout.write(
                f"  {'DRY ' if dry_run else ''}CREATE  {user.email} "
                f"({app.franchise_type}, {app.proposed_location}, {app.country})"
            )

            if not dry_run:
                FranchiseeProfile.objects.create(
                    user=user,
                    application=app,
                    franchise_type=app.franchise_type,
                    territory=app.proposed_location or app.city or app.country,
                    country=app.country,
                    operational_status="active",
                )
                # Ensure correct user role
                if user.user_role != "franchisee":
                    user.user_role = "franchisee"
                    user.save(update_fields=["user_role"])

            created += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would create' if dry_run else 'Created'} {created} profile(s), "
                f"skipped {skipped}."
            )
        )
