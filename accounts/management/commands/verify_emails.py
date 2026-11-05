"""
T&TG Trade Corporation — Verify all existing email addresses
Run this to mark all current users' emails as verified so they can set up 2FA.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Mark all existing user emails as verified in allauth'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        from allauth.account.models import EmailAddress

        users = User.objects.filter(is_active=True)
        verified = 0
        created = 0

        for user in users:
            if not user.email:
                continue
            # Demote any primary email that isn't this address (prevents unique constraint
            # violation on (user_id, primary=True) when creating a new primary record).
            EmailAddress.objects.filter(user=user, primary=True).exclude(
                email=user.email
            ).update(primary=False)

            obj, was_created = EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={
                    'primary':  True,
                    'verified': True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f'Created and verified: {user.email}')
            elif not obj.verified:
                verified += 1
                self.stdout.write(f'Verified: {user.email}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Created: {created}, Verified: {verified}, Total users: {users.count()}'
            )
        )
