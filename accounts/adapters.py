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

        Runs before allauth creates a new user.  If the social login's email
        already belongs to an existing account we connect them here, which
        prevents allauth from trying to INSERT a second primary email row and
        hitting the unique_primary_email constraint.
        """
        import logging
        logger = logging.getLogger(__name__)

        if sociallogin.is_existing:
            return

        # Prefer allauth's parsed email list (reliable for all providers).
        # Fall back to extra_data only if the list is empty.
        email = None
        for ea in sociallogin.email_addresses:
            if ea.primary or email is None:
                email = ea.email
        if not email:
            email = sociallogin.account.extra_data.get('email', '') or ''
        email = email.lower().strip()
        if not email:
            return

        try:
            from allauth.account.models import EmailAddress
            existing = EmailAddress.objects.get(email__iexact=email)
            sociallogin.connect(request, existing.user)
            logger.info(f'pre_social_login: connected {email} to existing user {existing.user_id}')
        except EmailAddress.DoesNotExist:
            pass  # New email — let allauth create the account normally
        except Exception as exc:
            logger.error(f'pre_social_login error for {email}: {exc}')


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
