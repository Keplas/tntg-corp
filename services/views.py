from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import ForexRate, InsurancePolicy, BrokerageAccount
from django.contrib.auth.decorators import login_required


def trade_ecommerce(request):
    """Landing page for Trade & E-Commerce section — also franchise hub."""
    from .models import FranchiseApplication
    forex_rates = ForexRate.objects.all()[:3]
    return render(request, 'services/trade_ecommerce.html', {
        'forex_rates': forex_rates,
        'franchise_types': FranchiseApplication.FRANCHISE_TYPE_CHOICES,
    })


def import_export(request):
    """Import & Export operations page."""
    return render(request, 'services/import_export.html')


def forex(request):
    from core.exchange_rates import fetch_live_rates, build_pairs
    from django.utils import timezone
    raw   = fetch_live_rates()
    pairs = build_pairs(raw)
    db_rates = ForexRate.objects.all()
    is_live   = raw is not None
    last_updated = timezone.now().strftime("%d %b %Y, %H:%M UTC")
    ctx = {
        'pairs':     pairs,
        'db_rates':  db_rates,
        'is_live':   is_live,
        'last_updated': last_updated,
        'raw_rates': raw,
        'has_live': bool(raw),
    }
    return render(request, 'services/forex.html', ctx)


# Legacy views kept for admin / back-office use — not shown in public nav
def insurance(request):
    return render(request, 'services/insurance.html')


def brokerage(request):
    rates = ForexRate.objects.all()
    return render(request, 'services/brokerage.html', {'rates': rates})


# ════════════════════════════════════════════════════════════════════════
# FRANCHISE APPLICATION & DASHBOARD
# ════════════════════════════════════════════════════════════════════════

def franchise_hub(request):
    """Franchise platform landing page — markets all 5 franchise types."""
    from .models import FranchiseApplication
    return render(request, 'services/franchise_hub.html', {
        'franchise_types': FranchiseApplication.FRANCHISE_TYPE_CHOICES,
    })


def franchise_apply(request):
    """Public franchise application form — anyone can apply."""
    from .models import FranchiseApplication
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            app = FranchiseApplication.objects.create(
                full_name           = d.get('full_name', '').strip(),
                email               = d.get('email', '').strip(),
                phone               = d.get('phone', '').strip(),
                country             = d.get('country', '').strip(),
                city                = d.get('city', '').strip(),
                company_name        = d.get('company_name', '').strip(),
                franchise_type      = d.get('franchise_type', 'cafe_kiosk'),
                investment_budget   = d.get('investment_budget', 'under_10k'),
                business_experience = d.get('business_experience', 'none'),
                proposed_location   = d.get('proposed_location', '').strip(),
                start_timeline      = d.get('start_timeline', 'exploring'),
                why_tntg            = d.get('why_tntg', '').strip(),
                additional_notes    = d.get('additional_notes', '').strip(),
                casl_consent        = d.get('casl_consent') == 'on',
                user                = request.user if request.user.is_authenticated else None,
            )
        except Exception as e:
            from django.contrib import messages as msg
            msg.error(request, f'Submission failed: {e}. Please try again or contact tom.grouptrade@gmail.com.')
            return redirect('franchise_apply')

        # Email Tom
        try:
            send_mail(
                subject=f'New Franchise Application #{app.ref()} — {app.get_franchise_type_display()} — {app.full_name}',
                message=(
                    f'New FRANCHISE APPLICATION received:\n\n'
                    f'Name:         {app.full_name}\n'
                    f'Company:      {app.company_name or "N/A"}\n'
                    f'Email:        {app.email}\n'
                    f'Phone:        {app.phone or "N/A"}\n'
                    f'Country:      {app.country}\n'
                    f'City:         {app.city or "N/A"}\n\n'
                    f'Franchise:    {app.get_franchise_type_display()}\n'
                    f'Budget:       {app.get_investment_budget_display()}\n'
                    f'Experience:   {app.get_business_experience_display()}\n'
                    f'Location:     {app.proposed_location}\n'
                    f'Timeline:     {app.get_start_timeline_display()}\n\n'
                    f'Why T&TG:\n{app.why_tntg}\n\n'
                    f'Notes:\n{app.additional_notes or "None"}\n\n'
                    f'Review at: https://tomtradecorp.com/franchise/dashboard/'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        # Confirmation to applicant
        try:
            send_mail(
                subject=f'Franchise Application {app.ref()} Received — T&TG Trade Corporation',
                message=(
                    f'Dear {app.full_name},\n\n'
                    f'Thank you for applying to franchise with T&TG Trade Corporation.\n\n'
                    f'Your reference number is: {app.ref()}\n\n'
                    f'Details submitted:\n'
                    f'  Franchise Type: {app.get_franchise_type_display()}\n'
                    f'  Location:       {app.proposed_location}\n'
                    f'  Timeline:       {app.get_start_timeline_display()}\n\n'
                    f'Our team will review your application and reach out within 3 business days.\n\n'
                    f'T&TG Trade Corporation\n'
                    f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                    f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=[app.email],
                fail_silently=True,
            )
        except Exception:
            pass

        from django.contrib import messages as msg
        msg.success(request,
            f'Your franchise application {app.ref()} has been received! '
            f'We will be in touch within 3 business days.')
        return redirect('franchise_apply')

    from .models import FranchiseApplication as FA
    return render(request, 'services/franchise_apply.html', {
        'franchise_types': FA.FRANCHISE_TYPE_CHOICES,
    })


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def franchise_dashboard(request):
    """Staff dashboard — manage all franchise applications."""
    from .models import FranchiseApplication

    status_filter = request.GET.get('status', '')
    type_filter   = request.GET.get('type', '')

    apps = FranchiseApplication.objects.all()
    if status_filter:
        apps = apps.filter(status=status_filter)
    if type_filter:
        apps = apps.filter(franchise_type=type_filter)

    counts = {
        'total':     FranchiseApplication.objects.count(),
        'pending':   FranchiseApplication.objects.filter(status='pending').count(),
        'reviewing': FranchiseApplication.objects.filter(status='reviewing').count(),
        'approved':  FranchiseApplication.objects.filter(status='approved').count(),
        'rejected':  FranchiseApplication.objects.filter(status='rejected').count(),
        'on_hold':   FranchiseApplication.objects.filter(status='on_hold').count(),
    }

    ctx = {
        'applications':   apps,
        'counts':         counts,
        'status_filter':  status_filter,
        'type_filter':    type_filter,
    }
    return render(request, 'services/franchise_dashboard.html', ctx)


@staff_member_required
def franchise_update_status(request, pk):
    """Staff updates status and notes on a franchise application."""
    from .models import FranchiseApplication
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    app = get_object_or_404(FranchiseApplication, pk=pk)
    if request.method == 'POST':
        new_status  = request.POST.get('status', app.status)
        admin_notes = request.POST.get('admin_notes', '').strip()
        app.status      = new_status
        app.admin_notes = admin_notes
        app.save(update_fields=['status', 'admin_notes', 'updated_at'])

        status_messages = {
            'reviewing': 'Your franchise application is now under review by our team.',
            'approved':  'Congratulations! Your franchise application has been APPROVED. Our team will contact you shortly to discuss next steps.',
            'rejected':  f'After careful review, we are unable to proceed with your franchise application at this time.\n\nReason: {admin_notes or "Please contact us for details."}',
            'on_hold':   'Your franchise application has been placed on hold. We will follow up with you soon.',
        }
        msg_text = status_messages.get(new_status)
        if msg_text:
            try:
                send_mail(
                    subject=f'Franchise Application {app.ref()} Update — T&TG Trade Corp',
                    message=(
                        f'Dear {app.full_name},\n\n{msg_text}\n\n'
                        f'Reference: {app.ref()}\n\n'
                        f'T&TG Trade Corporation\n'
                        f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                        f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                    ),
                    from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                    recipient_list=[app.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        # ── Auto-create FranchiseeProfile on first approval ──────────────────
        if new_status == 'approved' and app.user:
            from .models import FranchiseeProfile
            profile, created = FranchiseeProfile.objects.get_or_create(
                application=app,
                defaults=dict(
                    user          = app.user,
                    franchise_type= app.franchise_type,
                    territory     = app.proposed_location,
                    country       = app.country,
                    operational_status = 'setup',
                ),
            )
            if created:
                # Send franchisee welcome email
                try:
                    send_mail(
                        subject=f'Welcome to T&TG Franchise Network — {profile.display_name()}',
                        message=(
                            f'Dear {app.full_name},\n\n'
                            f'Your franchise application {app.ref()} has been approved and your '
                            f'franchisee account is now active.\n\n'
                            f'Your franchise details:\n'
                            f'  Reference:  {profile.ref()}\n'
                            f'  Type:       {profile.get_franchise_type_display()}\n'
                            f'  Territory:  {profile.territory}\n'
                            f'  Status:     {profile.get_operational_status_display()}\n\n'
                            f'Log in to your T&TG account to access your Franchise Hub:\n'
                            f'  https://tomtradecorp.com/franchise/my-store/\n\n'
                            f'Our team will be in touch to guide your setup.\n\n'
                            f'T&TG Trade Corporation\n'
                            f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                            f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                        ),
                        from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                        recipient_list=[app.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

        messages.success(request, f'Application {app.ref()} updated to {new_status}.')
    return redirect('franchise_dashboard')


# ════════════════════════════════════════════════════════════════════════
# FRANCHISEE STORE — personal dashboard for each approved franchisee
# ════════════════════════════════════════════════════════════════════════

# ── Franchisee self-registration ──────────────────────────────────────────────

def franchise_register(request):
    """
    Fast-track franchisee sign-up.
    Creates a CustomUser + FranchiseApplication (auto-approved) + FranchiseeProfile
    in a single step.  Linked from franchise_hub.html CTAs.
    """
    from accounts.models import CustomUser
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    from .models import FranchiseApplication, FranchiseeProfile
    from django.contrib.auth import login as auth_login
    from django.core.cache import cache

    # Pre-fill franchise type from ?type= query param (from card links)
    prefill_type = request.GET.get('type', '')

    if request.method == 'POST':
        d = request.POST

        # ── Honeypot ──────────────────────────────────────────────────────────
        if d.get('_hp_name', '').strip():
            return redirect('franchise_hub')

        # ══════════════════════════════════════════════════════════════════════
        # PATH A: Already logged-in TNTG user applying for a franchise
        # ══════════════════════════════════════════════════════════════════════
        if request.user.is_authenticated and not request.user.is_platform_admin:
            user = request.user

            # Already a franchisee?
            if hasattr(user, 'franchisee_profile'):
                messages.warning(request, 'You already have an active franchise hub.')
                return redirect('franchisee_store')

            # ── Required franchise fields ─────────────────────────────────────
            franchise_type    = d.get('franchise_type', '')
            proposed_location = d.get('proposed_location', '').strip()
            country           = d.get('country', '') or user.country
            if not franchise_type or not proposed_location or not country:
                messages.error(request, 'Please fill in all required franchise fields.')
                return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

            # ── Auto-approved application ─────────────────────────────────────
            app = FranchiseApplication.objects.create(
                user=user,
                full_name=user.get_full_name() or user.username,
                email=user.email,
                phone=user.phone,
                country=country,
                franchise_type=franchise_type,
                proposed_location=proposed_location,
                investment_budget=d.get('investment_budget', 'under_10k'),
                start_timeline=d.get('start_timeline', 'asap'),
                business_experience=d.get('business_experience', 'none'),
                why_tntg=d.get('why_tntg', 'Self-registered via franchisee portal.'),
                status='approved',
                admin_notes='Auto-approved via franchisee self-registration (existing user).',
            )

            # ── FranchiseeProfile ─────────────────────────────────────────────
            FranchiseeProfile.objects.create(
                user=user,
                application=app,
                franchise_type=franchise_type,
                territory=proposed_location,
                country=country,
                operational_status='setup',
            )

            # Upgrade role to franchisee if still set to a marketplace role
            if user.user_role not in ('franchisee', 'regional_manager'):
                user.user_role = 'franchisee'
                user.save(update_fields=['user_role'])

            messages.success(request,
                f'Welcome to T&TG Franchisee Network, {user.first_name or user.username}! '
                f'Your hub is ready.')
            return redirect('franchisee_store')

        # ══════════════════════════════════════════════════════════════════════
        # PATH B: New user — create account + franchise in one step
        # ══════════════════════════════════════════════════════════════════════

        # ── IP rate limit: 3 registrations / IP / hour ────────────────────────
        from accounts.views import _get_client_ip
        client_ip = _get_client_ip(request)
        rate_key  = f'freg_ip_{client_ip}'
        if cache.get(rate_key, 0) >= 3:
            messages.error(request, 'Too many registrations from your connection. Try again in an hour.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

        # ── Validate email ────────────────────────────────────────────────────
        email = d.get('email', '').lower().strip()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists. Please log in.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

        # ── Password ──────────────────────────────────────────────────────────
        pw1 = d.get('password', '')
        pw2 = d.get('confirm_password', '')
        if pw1 != pw2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})
        if len(pw1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

        # ── Required franchise fields ─────────────────────────────────────────
        franchise_type    = d.get('franchise_type', '')
        proposed_location = d.get('proposed_location', '').strip()
        country           = d.get('country', '')
        if not franchise_type or not proposed_location or not country:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'services/franchise_register.html', {'post': d, 'prefill_type': prefill_type})

        # ── Create user ───────────────────────────────────────────────────────
        import re
        base_username = re.sub(r'[^a-z0-9]', '', email.split('@')[0].lower()) or 'user'
        username = base_username
        suffix = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f'{base_username}{suffix}'
            suffix += 1

        cache.set(rate_key, cache.get(rate_key, 0) + 1, 3600)

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=pw1,
            is_active=True,
            first_name=d.get('first_name', '').strip(),
            last_name=d.get('last_name', '').strip(),
            phone=d.get('phone', '').strip(),
            country=country,
            user_role='franchisee',
        )

        # ── Auto-approved franchise application ───────────────────────────────
        app = FranchiseApplication.objects.create(
            user=user,
            full_name=user.get_full_name() or username,
            email=email,
            phone=user.phone,
            country=country,
            franchise_type=franchise_type,
            proposed_location=proposed_location,
            investment_budget=d.get('investment_budget', 'under_10k'),
            start_timeline=d.get('start_timeline', 'asap'),
            business_experience=d.get('business_experience', 'none'),
            why_tntg=d.get('why_tntg', 'Self-registered via franchisee portal.'),
            status='approved',
            admin_notes='Auto-approved via franchisee self-registration.',
        )

        # ── FranchiseeProfile — hub is immediately accessible ─────────────────
        FranchiseeProfile.objects.create(
            user=user,
            application=app,
            franchise_type=franchise_type,
            territory=proposed_location,
            country=country,
            operational_status='setup',
        )

        # ── Log in and redirect to hub ────────────────────────────────────────
        auth_login(request, user, backend='accounts.backends.FlexAuthBackend')
        messages.success(request,
            f'Welcome to T&TG Franchisee Network, {user.first_name or username}! '
            f'Your hub is ready.')
        return redirect('franchisee_store')

    return render(request, 'services/franchise_register.html', {
        'post': {},
        'prefill_type': prefill_type,
        'franchise_types':    FranchiseApplication.FRANCHISE_TYPE_CHOICES,
        'budget_choices':     FranchiseApplication.BUDGET_CHOICES,
        'timeline_choices':   FranchiseApplication.TIMELINE_CHOICES,
        'experience_choices': FranchiseApplication.EXPERIENCE_CHOICES,
        'countries': [('CA', 'Canada'), ('UG', 'Uganda'), ('KE', 'Kenya')],
    })


# ════════════════════════════════════════════════════════════════════════

from .decorators import franchisee_required

@franchisee_required
def franchisee_store(request):
    """Personal franchise hub — visible only to the account owner."""
    from django.utils import timezone
    from django.db.models import Sum, Count
    from .models import FranchiseApplication
    import datetime

    profile = request.user.franchisee_profile
    now = timezone.now()
    this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    products = profile.products.all()
    orders   = profile.orders.exclude(status__in=['cancelled', 'refunded'])
    mtd      = orders.filter(placed_at__gte=this_month).aggregate(
                   revenue=Sum('total'), count=Count('id'))

    ctx = {
        'profile':           profile,
        'app':               profile.application,
        'product_count':     products.count(),
        'approved_products': products.filter(status='approved').count(),
        'orders_mtd':        mtd['count'] or 0,
        'revenue_mtd':       mtd['revenue'] or 0,
        'new_orders':        profile.orders.filter(status='new').count(),
        'stock_pending':     profile.stock_requests.filter(
                                status__in=['submitted', 'acknowledged', 'processing']
                             ).count(),
        'customer_count':    profile.customers.count(),
    }
    return render(request, 'services/franchisee_store.html', ctx)


@login_required
def my_franchise_applications(request):
    """Logged-in user — see their own franchise application history."""
    from .models import FranchiseApplication
    apps = FranchiseApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/my_franchise_applications.html', {'applications': apps})


def cooperation_program(request):
    # Page consolidated into the Onboarding Accelerator (/join/)
    return redirect('join_program', permanent=True)


def join_program(request):
    return render(request, 'services/join_program.html')


# ════════════════════════════════════════════════════════════════════════
# PARTNERSHIP APPLICATION
# ════════════════════════════════════════════════════════════════════════

def partnership_apply(request):
    """Public partnership application form — suppliers, manufacturers, logistics, etc."""
    from .models import PartnershipApplication
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            app = PartnershipApplication.objects.create(
                full_name           = d.get('full_name', '').strip(),
                email               = d.get('email', '').strip(),
                phone               = d.get('phone', '').strip(),
                country             = d.get('country', '').strip(),
                city                = d.get('city', '').strip(),
                company_name        = d.get('company_name', '').strip(),
                partnership_type    = d.get('partnership_type', 'other'),
                company_description = d.get('company_description', '').strip(),
                what_you_offer      = d.get('what_you_offer', '').strip(),
                annual_capacity     = d.get('annual_capacity', 'na'),
                start_timeline      = d.get('start_timeline', 'exploring'),
                why_tntg            = d.get('why_tntg', '').strip(),
                additional_notes    = d.get('additional_notes', '').strip(),
                casl_consent        = d.get('casl_consent') == 'on',
                user                = request.user if request.user.is_authenticated else None,
            )
        except Exception as e:
            from django.contrib import messages as msg
            msg.error(request, f'Submission failed: {e}. Please try again or contact tom.grouptrade@gmail.com.')
            return redirect('partnership_apply')

        # Email Tom
        try:
            send_mail(
                subject=f'New Partnership Application #{app.ref()} — {app.get_partnership_type_display()} — {app.full_name}',
                message=(
                    f'New PARTNERSHIP APPLICATION received:\n\n'
                    f'Name:         {app.full_name}\n'
                    f'Company:      {app.company_name or "N/A"}\n'
                    f'Email:        {app.email}\n'
                    f'Phone:        {app.phone or "N/A"}\n'
                    f'Country:      {app.country}\n'
                    f'City:         {app.city or "N/A"}\n\n'
                    f'Partnership:  {app.get_partnership_type_display()}\n'
                    f'Capacity:     {app.get_annual_capacity_display()}\n'
                    f'Timeline:     {app.get_start_timeline_display()}\n\n'
                    f'About the company:\n{app.company_description}\n\n'
                    f'What they offer:\n{app.what_you_offer}\n\n'
                    f'Why T&TG:\n{app.why_tntg}\n\n'
                    f'Notes:\n{app.additional_notes or "None"}\n'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        # Confirmation to applicant
        try:
            send_mail(
                subject=f'Partnership Application {app.ref()} Received — T&TG Trade Corporation',
                message=(
                    f'Dear {app.full_name},\n\n'
                    f'Thank you for your interest in partnering with T&TG Trade Corporation.\n\n'
                    f'Your reference number is: {app.ref()}\n\n'
                    f'Details submitted:\n'
                    f'  Partnership Type: {app.get_partnership_type_display()}\n'
                    f'  Timeline:         {app.get_start_timeline_display()}\n\n'
                    f'Our team will review your application and reach out within 3 business days.\n\n'
                    f'T&TG Trade Corporation\n'
                    f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                    f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=[app.email],
                fail_silently=True,
            )
        except Exception:
            pass

        from django.contrib import messages as msg
        msg.success(request,
            f'Your partnership application {app.ref()} has been received! '
            f'We will be in touch within 3 business days.')
        return redirect('partnership_apply')

    from .models import PartnershipApplication as PA
    return render(request, 'services/partnership_apply.html', {
        'partnership_types': PA.PARTNERSHIP_TYPE_CHOICES,
        'capacity_choices':  PA.CAPACITY_CHOICES,
        'timeline_choices':  PA.TIMELINE_CHOICES,
    })


# ════════════════════════════════════════════════════════════════════════
# FRANCHISE PHASE 2 VIEWS
# ════════════════════════════════════════════════════════════════════════

def _get_franchisee(request):
    """Return (profile, app) or raise redirect if not franchisee."""
    from .models import FranchiseeProfile
    try:
        profile = request.user.franchisee_profile
        return profile, profile.application
    except FranchiseeProfile.DoesNotExist:
        return None, None


@login_required
def franchise_my_products(request):
    """Phase 2 — My Products: franchisee product catalogue."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    products = profile.products.all()
    return render(request, 'services/franchise_products.html', {
        'profile': profile,
        'app': app,
        'products': products,
        'approved_count': products.filter(status='approved').count(),
        'low_stock_count': sum(1 for p in products if p.is_low_stock and p.status == 'approved'),
    })


@login_required
def franchise_orders(request):
    """Phase 2 — Orders: list and fulfil customer orders."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    status_filter = request.GET.get('status', '')
    orders = profile.orders.all()
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'services/franchise_orders.html', {
        'profile': profile,
        'app': app,
        'orders': orders,
        'status_filter': status_filter,
        'new_count': profile.orders.filter(status='new').count(),
        'processing_count': profile.orders.filter(status='processing').count(),
    })


@login_required
def franchise_order_detail(request, pk):
    """Phase 2 — Order detail / fulfillment update."""
    profile, app = _get_franchisee(request)
    if profile is None:
        return redirect('franchisee_store')

    order = get_object_or_404(profile.orders, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed = ['confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status in allowed:
            order.status = new_status
            order.notes = request.POST.get('notes', order.notes)
            order.save()
            messages.success(request, f'Order {order.ref} updated to {order.get_status_display()}.')
        return redirect('franchise_order_detail', pk=pk)

    return render(request, 'services/franchise_order_detail.html', {
        'profile': profile,
        'app': app,
        'order': order,
    })


@login_required
def franchise_sales_reports(request):
    """Phase 2 — Sales Reports: monthly/annual territory revenue."""
    from django.utils import timezone
    from django.db.models import Sum, Count
    import datetime

    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_year_start  = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    orders = profile.orders.exclude(status__in=['cancelled', 'refunded'])

    mtd = orders.filter(placed_at__gte=this_month_start).aggregate(
        revenue=Sum('total'), count=Count('id')
    )
    ytd = orders.filter(placed_at__gte=this_year_start).aggregate(
        revenue=Sum('total'), count=Count('id')
    )

    # Last 6 months breakdown
    months = []
    for i in range(5, -1, -1):
        d = (now.replace(day=1) - datetime.timedelta(days=i * 28)).replace(day=1)
        end = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        agg = orders.filter(placed_at__gte=d, placed_at__lt=end).aggregate(
            revenue=Sum('total'), count=Count('id')
        )
        months.append({
            'label': d.strftime('%b'),
            'revenue': float(agg['revenue'] or 0),
            'count': agg['count'] or 0,
        })

    return render(request, 'services/franchise_reports.html', {
        'profile': profile,
        'app': app,
        'mtd_revenue': mtd['revenue'] or 0,
        'mtd_orders':  mtd['count']   or 0,
        'ytd_revenue': ytd['revenue'] or 0,
        'ytd_orders':  ytd['count']   or 0,
        'months': months,
        'recent_orders': orders.order_by('-placed_at')[:10],
    })


@login_required
def franchise_inventory(request):
    """Phase 2 — Inventory & Supply: submit stock replenishment requests."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    from .models import StockRequest
    from django.utils import timezone

    if request.method == 'POST':
        product_id   = request.POST.get('product_id')
        product_name = request.POST.get('product_name', '').strip()
        qty          = request.POST.get('quantity', '').strip()
        urgency      = request.POST.get('urgency', 'standard')
        notes        = request.POST.get('notes', '').strip()

        if not product_name or not qty or not qty.isdigit() or int(qty) < 1:
            messages.error(request, 'Please provide a valid product name and quantity.')
        else:
            product_obj = None
            if product_id:
                try:
                    product_obj = profile.products.get(pk=int(product_id), status='approved')
                except Exception:
                    pass

            sr = StockRequest.objects.create(
                franchisee=profile,
                product=product_obj,
                product_name=product_name,
                quantity_requested=int(qty),
                urgency=urgency,
                notes=notes,
                status='submitted',
                submitted_at=timezone.now(),
            )
            messages.success(request,
                f'Stock request {sr.ref} submitted to HQ. '
                f'Expected delivery: {sr.get_urgency_display()}.')
        return redirect('franchise_inventory')

    stock_requests = profile.stock_requests.all()
    products = profile.products.filter(status='approved')

    return render(request, 'services/franchise_inventory.html', {
        'profile': profile,
        'app': app,
        'stock_requests': stock_requests,
        'products': products,
        'pending_count': stock_requests.filter(status__in=['submitted','acknowledged','processing']).count(),
    })


# ──────────────────────────────────────────────────────────────
#  PHASE 3 — MY CUSTOMERS CRM
# ──────────────────────────────────────────────────────────────

@franchisee_required
def franchise_customers(request):
    """CRM — customer list with optional search."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    from .models import FranchiseeCustomer
    q = request.GET.get('q', '').strip()
    customers = profile.customers.all()
    if q:
        customers = customers.filter(
            models.Q(full_name__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(phone__icontains=q) |
            models.Q(company_name__icontains=q)
        )

    return render(request, 'services/franchise_customers.html', {
        'profile': profile,
        'app': app,
        'customers': customers,
        'q': q,
        'total': profile.customers.count(),
        'business_count': profile.customers.filter(customer_type='business').count(),
    })


@franchisee_required
def franchise_customer_detail(request, pk):
    """CRM — customer detail + linked orders (matched by email)."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    from .models import FranchiseeCustomer, FranchiseeOrder
    try:
        customer = profile.customers.get(pk=pk)
    except FranchiseeCustomer.DoesNotExist:
        messages.error(request, 'Customer not found.')
        return redirect('franchise_customers')

    linked_orders = []
    if customer.email:
        linked_orders = profile.orders.filter(
            customer_email__iexact=customer.email
        ).order_by('-placed_at')

    return render(request, 'services/franchise_customer_detail.html', {
        'profile': profile,
        'app': app,
        'customer': customer,
        'linked_orders': linked_orders,
    })


@franchisee_required
def franchise_customer_add(request):
    """CRM — add a new customer."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    from .models import FranchiseeCustomer

    if request.method == 'POST':
        full_name     = request.POST.get('full_name', '').strip()
        email         = request.POST.get('email', '').strip()
        phone         = request.POST.get('phone', '').strip()
        company_name  = request.POST.get('company_name', '').strip()
        customer_type = request.POST.get('customer_type', 'individual')
        address       = request.POST.get('address', '').strip()
        notes         = request.POST.get('notes', '').strip()

        if not full_name:
            messages.error(request, 'Full name is required.')
        elif email and profile.customers.filter(email__iexact=email).exists():
            messages.error(request, f'A customer with email {email} already exists.')
        else:
            cust = FranchiseeCustomer.objects.create(
                franchisee=profile,
                full_name=full_name,
                email=email,
                phone=phone,
                company_name=company_name,
                customer_type=customer_type,
                address=address,
                notes=notes,
            )
            messages.success(request, f'Customer {cust.full_name} added successfully.')
            return redirect('franchise_customer_detail', pk=cust.pk)
    else:
        # Pre-fill from order if coming from order detail
        order_email = request.GET.get('email', '')
        order_name  = request.GET.get('name', '')

    return render(request, 'services/franchise_customer_form.html', {
        'profile': profile,
        'app': app,
        'form_action': 'add',
        'prefill_email': request.GET.get('email', ''),
        'prefill_name': request.GET.get('name', ''),
    })


@franchisee_required
def franchise_customer_edit(request, pk):
    """CRM — edit customer details."""
    profile, app = _get_franchisee(request)
    if profile is None:
        messages.error(request, 'You do not have an active franchise profile.')
        return redirect('franchisee_store')

    from .models import FranchiseeCustomer
    try:
        customer = profile.customers.get(pk=pk)
    except FranchiseeCustomer.DoesNotExist:
        messages.error(request, 'Customer not found.')
        return redirect('franchise_customers')

    if request.method == 'POST':
        full_name     = request.POST.get('full_name', '').strip()
        email         = request.POST.get('email', '').strip()
        phone         = request.POST.get('phone', '').strip()
        company_name  = request.POST.get('company_name', '').strip()
        customer_type = request.POST.get('customer_type', 'individual')
        address       = request.POST.get('address', '').strip()
        notes         = request.POST.get('notes', '').strip()

        if not full_name:
            messages.error(request, 'Full name is required.')
        elif (email and email.lower() != customer.email.lower() and
              profile.customers.filter(email__iexact=email).exists()):
            messages.error(request, f'Another customer already has email {email}.')
        else:
            customer.full_name    = full_name
            customer.email        = email
            customer.phone        = phone
            customer.company_name = company_name
            customer.customer_type = customer_type
            customer.address      = address
            customer.notes        = notes
            customer.save()
            messages.success(request, 'Customer updated.')
            return redirect('franchise_customer_detail', pk=customer.pk)

    return render(request, 'services/franchise_customer_form.html', {
        'profile': profile,
        'app': app,
        'customer': customer,
        'form_action': 'edit',
    })
