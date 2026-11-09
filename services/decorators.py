"""
Franchise access control decorators.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def franchisee_required(view_func):
    """
    Allow access only to logged-in users with an active FranchiseeProfile.
    Redirects to login if not authenticated, or to franchise hub if no profile.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')

        try:
            profile = request.user.franchisee_profile
        except Exception:
            messages.warning(
                request,
                'You do not have an active franchisee account. '
                'Apply to join the T&TG franchise network.'
            )
            return redirect('franchise_hub')

        if profile.operational_status == 'terminated':
            messages.error(request, 'Your franchise account has been terminated. Please contact HQ.')
            return redirect('franchise_hub')

        return view_func(request, *args, **kwargs)

    return wrapper
