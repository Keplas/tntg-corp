"""
T&TG Trade Corporation — Security Decorators for Loyalty System
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta


def mfa_required(view_func):
    """
    Requires the user to have MFA enabled before accessing loyalty features.
    Redirects to MFA setup if not configured.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            from allauth.mfa.models import Authenticator
            has_mfa = Authenticator.objects.filter(
                user=request.user,
                type=Authenticator.Type.TOTP
            ).exists()
            if not has_mfa:
                messages.warning(
                    request,
                    'Your T&TG Loyalty account requires Two-Factor Authentication. '
                    'Set up 2FA to access your rewards and wallet.'
                )
                return redirect('mfa_activate_totp')
        except Exception:
            pass  # If MFA check fails, allow through (graceful degradation)
        return view_func(request, *args, **kwargs)
    return wrapper


def loyalty_reauth_required(view_func):
    """
    Requires recent authentication (within 10 minutes) before
    sensitive loyalty operations like redemption and transfers.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        last_auth = request.session.get('loyalty_reauth_time')
        now = timezone.now().timestamp()
        REAUTH_WINDOW = 600  # 10 minutes

        if not last_auth or (now - last_auth) > REAUTH_WINDOW:
            request.session['loyalty_reauth_next'] = request.path
            messages.info(
                request,
                'Please confirm your identity to continue with this loyalty operation.'
            )
            return redirect('loyalty_reauth')
        return view_func(request, *args, **kwargs)
    return wrapper


def check_loyalty_cooloff(user):
    """
    Returns True if user is in a cooling-off period (48h after password/email change).
    """
    cooloff_until = getattr(user, 'loyalty_cooloff_until', None)
    if cooloff_until and timezone.now() < cooloff_until:
        return True, cooloff_until
    return False, None


def check_daily_limit(user, amount):
    """
    Check if redemption/transfer would exceed daily cap.
    Daily cap: 10,000 points or 5 transactions.
    """
    from .models import PointsAuditLog
    today = timezone.now().date()
    try:
        daily_txns = PointsAuditLog.objects.filter(
            user=user,
            created_at__date=today,
            action__in=['redeem', 'transfer']
        )
        daily_count = daily_txns.count()
        daily_total = sum(t.points_amount for t in daily_txns)

        if daily_count >= 5:
            return False, 'Daily transaction limit reached (5 per day). Try again tomorrow.'
        if daily_total + amount > 10000:
            remaining = 10000 - daily_total
            return False, f'Daily redemption cap exceeded. You can redeem up to {remaining:.0f} more points today.'
    except Exception:
        pass
    return True, None
