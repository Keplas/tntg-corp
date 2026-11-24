"""
B2B Referral Platform views — Authorized Resellers
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count


# ── Public landing ────────────────────────────────────────────────────────────

def b2b_landing(request):
    """B2B Referral Platform marketing page."""
    return render(request, 'services/b2b_landing.html', {
        'page': 'b2b',
    })


# ── Application ───────────────────────────────────────────────────────────────

def b2b_apply(request):
    """Public B2B partner application form."""
    from .models import B2BApplication
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            app = B2BApplication.objects.create(
                full_name              = d.get('full_name', '').strip(),
                email                  = d.get('email', '').strip(),
                phone                  = d.get('phone', '').strip(),
                country                = d.get('country', '').strip(),
                city                   = d.get('city', '').strip(),
                company_name           = d.get('company_name', '').strip(),
                business_type          = d.get('business_type', 'small_business'),
                store_type             = d.get('store_type', 'physical'),
                store_address          = d.get('store_address', '').strip(),
                website                = d.get('website', '').strip(),
                monthly_order_estimate = d.get('monthly_order_estimate', 'under_500'),
                years_in_business      = d.get('years_in_business', 'none'),
                products_interest      = d.get('products_interest', '').strip(),
                why_partner            = d.get('why_partner', '').strip(),
                additional_notes       = d.get('additional_notes', '').strip(),
                casl_consent           = d.get('casl_consent') == 'on',
                user                   = request.user if request.user.is_authenticated else None,
            )
        except Exception as e:
            messages.error(request, f'Submission failed: {e}. Please try again or contact tom.grouptrade@gmail.com.')
            return redirect('b2b_apply')

        # Notify admin
        try:
            send_mail(
                subject=f'New B2B Reseller Application #{app.ref()} — {app.full_name}',
                message=(
                    f'New B2B RESELLER APPLICATION received:\n\n'
                    f'Name:          {app.full_name}\n'
                    f'Company:       {app.company_name or "N/A"}\n'
                    f'Email:         {app.email}\n'
                    f'Phone:         {app.phone or "N/A"}\n'
                    f'Country:       {app.country}\n'
                    f'City:          {app.city or "N/A"}\n\n'
                    f'Business Type: {app.get_business_type_display()}\n'
                    f'Store Type:    {app.get_store_type_display()}\n'
                    f'Store Address: {app.store_address or "N/A"}\n'
                    f'Website:       {app.website or "N/A"}\n\n'
                    f'Monthly Order: {app.get_monthly_order_estimate_display()}\n'
                    f'Experience:    {app.get_years_in_business_display()}\n\n'
                    f'Products Interest:\n{app.products_interest}\n\n'
                    f'Why Partner:\n{app.why_partner}\n\n'
                    f'Notes: {app.additional_notes or "None"}\n'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request,
            f'Application #{app.ref()} submitted! Our team will review it within 3 business days.')
        return redirect('b2b_apply_success')

    return render(request, 'services/b2b_apply.html', {
        'prefill': {
            'full_name':  request.user.get_full_name() if request.user.is_authenticated else '',
            'email':      request.user.email if request.user.is_authenticated else '',
            'phone':      getattr(request.user, 'phone', '') if request.user.is_authenticated else '',
            'country':    getattr(request.user, 'country', '') if request.user.is_authenticated else '',
            'city':       getattr(request.user, 'city', '') if request.user.is_authenticated else '',
        },
    })


def b2b_apply_success(request):
    return render(request, 'services/b2b_apply_success.html')


# ── Referral tracking ─────────────────────────────────────────────────────────

def b2b_referral_track(request, code):
    """
    Store referral code in session and redirect to marketplace.
    Every purchase made in the same session is attributed to this reseller.
    """
    from .models import B2BProfile
    try:
        profile = B2BProfile.objects.get(referral_code=code, status='active')
        request.session['b2b_ref_code'] = code
        request.session['b2b_ref_id']   = profile.pk
        request.session.modified = True
    except B2BProfile.DoesNotExist:
        pass
    return redirect('marketplace')


# ── Reseller portal ───────────────────────────────────────────────────────────

@login_required
def b2b_portal(request):
    """Personal B2B reseller dashboard."""
    from .models import B2BProfile, B2BReferral

    try:
        profile = request.user.b2b_profile
    except Exception:
        messages.info(request, 'You are not yet an Authorized Reseller. Apply below.')
        return redirect('b2b_apply')

    referrals = B2BReferral.objects.filter(reseller=profile)
    confirmed = referrals.filter(status__in=['confirmed', 'paid'])
    pending   = referrals.filter(status='pending')

    total_commission = confirmed.aggregate(total=Sum('commission'))['total'] or 0
    pending_commission = pending.aggregate(total=Sum('commission'))['total'] or 0

    ctx = {
        'profile':            profile,
        'referrals':          referrals[:30],
        'total_commission':   total_commission,
        'pending_commission': pending_commission,
        'referral_count':     referrals.count(),
        'confirmed_count':    confirmed.count(),
        'referral_url':       profile.referral_url(request),
    }
    return render(request, 'services/b2b_portal.html', ctx)


@login_required
def b2b_my_applications(request):
    """List this user's B2B applications."""
    from .models import B2BApplication
    apps = B2BApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/b2b_my_applications.html', {'applications': apps})
