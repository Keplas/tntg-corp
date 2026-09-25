"""
T&TG Trade Corporation — 2FA Enforcement Middleware
Staff and admin users must have TOTP 2FA enabled
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


EXEMPT_URLS = [
    '/accounts/2fa/',
    '/accounts/login/',
    '/accounts/logout/',
    '/accounts/email/',
    '/accounts/confirm-email/',
    '/admin/login/',
]


class EnforceMFAForStaffMiddleware:
    """
    Redirects staff/admin users to set up 2FA if not already configured.
    Regular users are not affected.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if (
            user.is_authenticated
            and (user.is_staff or user.is_superuser)
            and not any(request.path.startswith(u) for u in EXEMPT_URLS)
        ):
            try:
                from allauth.mfa.models import Authenticator
                has_totp = Authenticator.objects.filter(
                    user=user,
                    type=Authenticator.Type.TOTP
                ).exists()
                if not has_totp:
                    messages.warning(
                        request,
                        'Staff accounts require Two-Factor Authentication. Please set up 2FA to continue.'
                    )
                    return redirect('/accounts/2fa/totp/activate/')
            except Exception:
                pass

        return self.get_response(request)
