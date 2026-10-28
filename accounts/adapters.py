"""
T&TG Trade Corporation — Custom Allauth Adapters
Handles user creation from both email/password and social login
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return True

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        # Assign to Consumer group by default
        if commit:
            user.save()
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='Consumer')
            user.groups.add(group)
        return user

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_staff or user.is_superuser:
            return '/accounts/dashboard/'
        return '/accounts/dashboard/'

    def send_mail(self, template_prefix, email, context):
        import logging
        logger = logging.getLogger(__name__)
        context['site_name'] = 'T&TG Trade Corporation'
        context['domain'] = 'tomtradecorp.com'
        try:
            super().send_mail(template_prefix, email, context)
        except Exception as e:
            logger.error(f'T&TG email send failed to {email}: {e}')
            # Do not raise — allow login/signup to continue even if email fails


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Assign to Consumer group by default for social signups
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='Consumer')
        user.groups.add(group)
        return user

    def pre_social_login(self, request, sociallogin):
        """Connect social account to existing account if email matches.

        Runs before allauth creates a new user.  We need to:
        1. Find the existing user by email
        2. Ensure account_emailaddress has a row for them (get_or_create)
        3. Connect the social login — this sets is_existing=True so allauth
           skips process_signup() and never tries to INSERT a duplicate email.
        """
        import logging
        logger = logging.getLogger(__name__)

        if sociallogin.is_existing:
            return

        # Prefer allauth's parsed email list (reliable for all providers).
        email = None
        for ea in (sociallogin.email_addresses or []):
            if ea.primary or email is None:
                email = ea.email
        if not email:
            email = sociallogin.account.extra_data.get('email', '') or ''
        email = email.lower().strip()
        if not email:
            return

        from django.contrib.auth import get_user_model
        from allauth.account.models import EmailAddress

        User = get_user_model()

        # Try to find via EmailAddress table first
        try:
            ea = EmailAddress.objects.get(email__iexact=email, primary=True)
            sociallogin.connect(request, ea.user)
            logger.info(f'pre_social_login: connected {email} via EmailAddress to user {ea.user_id}')
            return
        except EmailAddress.DoesNotExist:
            pass
        except Exception as exc:
            logger.error(f'pre_social_login EmailAddress lookup error: {exc}')
            return

        # Fall back: user exists in accounts_customuser but has no EmailAddress row
        try:
            user = User.objects.get(email__iexact=email)
            # Use the canonical stored email casing.  get_or_create with our
            # lowercased 'email' fails because allauth's unique_primary_email
            # index uses Lower(), so: get("john@...") misses "John@...", then
            # create("john@..") hits IntegrityError, then re-get also misses →
            # Django re-raises DoesNotExist instead of returning the row.
            canonical_email = user.email
            from django.db import IntegrityError
            if not EmailAddress.objects.filter(
                user=user, email__iexact=canonical_email, primary=True
            ).exists():
                try:
                    EmailAddress.objects.create(
                        user=user, email=canonical_email,
                        primary=True, verified=True,
                    )
                except IntegrityError:
                    pass  # race condition or duplicate — row exists, safe to proceed
            sociallogin.connect(request, user)
            logger.info(f'pre_social_login: connected {email} via CustomUser to user {user.pk}')
        except User.DoesNotExist:
            pass  # Genuinely new user — allauth handles signup normally
        except Exception as exc:
            logger.error(f'pre_social_login fallback error for {email}: {exc}')


class CustomMFAAdapter:
    """
    Disables the 2FA prompt during sign in.
    2FA is enforced only at the wallet layer via the mfa_required decorator.
    """
    def __init__(self, request=None):
        self.request = request

    def is_mfa_enabled(self, user, types=None):
        return False

    def __getattr__(self, name):
        from allauth.mfa.adapter import DefaultMFAAdapter
        base = DefaultMFAAdapter.__new__(DefaultMFAAdapter)
        base.request = self.request
        return getattr(base, name)
