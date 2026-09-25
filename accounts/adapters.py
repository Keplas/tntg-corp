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
        context['site_name'] = 'T&TG Trade Corporation'
        context['domain'] = 'tomtradecorp.com'
        super().send_mail(template_prefix, email, context)


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
        """Connect social account to existing account if email matches"""
        if sociallogin.is_existing:
            return
        from allauth.account.models import EmailAddress
        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if not email:
                return
            existing = EmailAddress.objects.get(email__iexact=email)
            sociallogin.connect(request, existing.user)
        except EmailAddress.DoesNotExist:
            pass
