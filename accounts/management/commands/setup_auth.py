"""
T&TG Trade Corporation — Setup authentication providers
Run on every deploy to ensure Site and SocialApp records exist
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Set up allauth Site and social auth providers'

    def handle(self, *args, **kwargs):
        # Update default site
        site, _ = Site.objects.update_or_create(
            id=1,
            defaults={
                'domain': 'tomtradecorp.com',
                'name':   'T&TG Trade Corporation',
            }
        )
        self.stdout.write(f'Site updated: {site.domain}')

        # Create Google social app
        google_id     = os.environ.get('GOOGLE_CLIENT_ID', '')
        google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        if google_id and google_secret:
            from allauth.socialaccount.models import SocialApp
            app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name':      'Google',
                    'client_id': google_id,
                    'secret':    google_secret,
                }
            )
            if not created:
                app.client_id = google_id
                app.secret    = google_secret
                app.save()
            app.sites.add(site)
            self.stdout.write(f'Google OAuth {"created" if created else "updated"}')
        else:
            self.stdout.write('GOOGLE_CLIENT_ID not set — skipping Google OAuth setup')

        # Create Microsoft social app
        ms_id     = os.environ.get('MICROSOFT_CLIENT_ID', '')
        ms_secret = os.environ.get('MICROSOFT_CLIENT_SECRET', '')

        if ms_id and ms_secret:
            from allauth.socialaccount.models import SocialApp
            app, created = SocialApp.objects.get_or_create(
                provider='microsoft',
                defaults={
                    'name':      'Microsoft',
                    'client_id': ms_id,
                    'secret':    ms_secret,
                }
            )
            if not created:
                app.client_id = ms_id
                app.secret    = ms_secret
                app.save()
            app.sites.add(site)
            self.stdout.write(f'Microsoft OAuth {"created" if created else "updated"}')
        else:
            self.stdout.write('MICROSOFT_CLIENT_ID not set — skipping Microsoft OAuth setup')

        # Create role groups
        from django.contrib.auth.models import Group
        for name in ['Admin', 'Staff', 'B2B Partner', 'Consumer']:
            Group.objects.get_or_create(name=name)
        self.stdout.write('Role groups confirmed')

        self.stdout.write(self.style.SUCCESS('Auth setup complete'))
