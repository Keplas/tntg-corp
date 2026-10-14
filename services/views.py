from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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

        messages.success(request, f'Application {app.ref()} updated to {new_status}.')
    return redirect('franchise_dashboard')


@login_required
def my_franchise_applications(request):
    """Logged-in user — see their own franchise application history."""
    from .models import FranchiseApplication
    apps = FranchiseApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/my_franchise_applications.html', {'applications': apps})


def cooperation_program(request):
    return render(request, 'services/cooperation_program.html')


def join_program(request):
    return render(request, 'services/join_program.html')
