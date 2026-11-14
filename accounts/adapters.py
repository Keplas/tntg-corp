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

    def clean_email(self, email):
        """Block disposable / throwaway email domains at the allauth layer."""
        from django.core.exceptions import ValidationError
        from accounts.views import _DISPOSABLE_DOMAINS
        email = super().clean_email(email)
        domain = email.split('@')[-1].lower() if '@' in email else ''
        if domain in _DISPOSABLE_DOMAINS:
            raise ValidationError(
                'Temporary or disposable email addresses are not allowed. '
                'Please use a real, active email address.'
            )
        return email

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
        """
        Email/password login redirect — staff go to admin, everyone else to dashboard.
        (Google OAuth uses CustomSocialAccountAdapter.get_login_redirect_url instead.)
        """
        user = request.user
        if user.is_staff or user.is_superuser:
            return '/admin/'
        try:
            if user.franchisee_profile:
                return '/franchise/my-store/'
        except Exception:
            pass
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

    def get_login_redirect_url(self, request):
        """
        Google / Microsoft OAuth redirect — never send to /admin/.
        Staff who sign in via social should land on the dashboard like any user.
        """
        user = request.user
        try:
            if user.franchisee_profile:
                return '/franchise/my-store/'
        except Exception:
            pass
        return '/accounts/dashboard/'

    def pre_social_login(self, request, sociallogin):
        """Connect social account to existing account if email matches.

        Runs before allauth creates a new user.  We need to:
        1. Validate that Google supplied a verified email address
        2. Find the existing user by email
        3. Ensure account_emailaddress has a row for them (get_or_create)
        4. Connect the social login — this sets is_existing=True so allauth
           skips process_signup() and never tries to INSERT a duplicate email.
        """
        import logging
        from django.contrib import messages as django_messages
        from allauth.exceptions import ImmediateHttpResponse
        from django.shortcuts import redirect
        logger = logging.getLogger(__name__)

        # ── 1. Extract email from Google's response ───────────────────────────
        # Prefer allauth's parsed email list (reliable for all providers).
        email = None
        for ea in (sociallogin.email_addresses or []):
            if ea.primary or email is None:
                email = ea.email
        if not email:
            email = sociallogin.account.extra_data.get('email', '') or ''
        email = email.lower().strip()

        # ── 2. Require a non-empty email ──────────────────────────────────────
        if not email:
            django_messages.error(
                request,
                'Your Google account does not have a verified email address. '
                'Please add one to your Google account and try again.'
            )
            raise ImmediateHttpResponse(redirect('account_login'))

        # ── 3. Require Google to have verified the email ──────────────────────
        extra = sociallogin.account.extra_data or {}
        email_verified = extra.get('email_verified', True)  # Google always sends this
        if not email_verified:
            django_messages.error(
                request,
                f'The email address {email} has not been verified by Google. '
                'Please verify it in your Google account settings and try again.'
            )
            raise ImmediateHttpResponse(redirect('account_login'))

        # ── 4. Block disposable / throwaway email domains ─────────────────────
        try:
            from accounts.views import _DISPOSABLE_DOMAINS
            domain = email.split('@')[-1].lower() if '@' in email else ''
            if domain in _DISPOSABLE_DOMAINS:
                django_messages.error(
                    request,
                    'Temporary or disposable email addresses are not allowed. '
                    'Please sign in with a real, active Google account.'
                )
                raise ImmediateHttpResponse(redirect('account_login'))
        except ImmediateHttpResponse:
            raise
        except Exception:
            pass  # If import fails for any reason, don't block login

        if sociallogin.is_existing:
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
