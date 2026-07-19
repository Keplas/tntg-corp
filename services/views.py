from django.shortcuts import render
from .models import ForexRate, InsurancePolicy, BrokerageAccount
from django.contrib.auth.decorators import login_required


def trade_ecommerce(request):
    """Landing page for Trade & E-Commerce section."""
    forex_rates = ForexRate.objects.all()[:3]
    return render(request, 'services/trade_ecommerce.html', {'forex_rates': forex_rates})


def import_export(request):
    """Import & Export operations page."""
    return render(request, 'services/import_export.html')


def forex(request):
    """Live exchange rates — powered by Open Exchange Rates API."""
    from core.exchange_rates import fetch_live_rates, build_pairs
    raw   = fetch_live_rates()
    pairs = build_pairs(raw)
    # Also pass DB rates as fallback display
    db_rates = ForexRate.objects.all()
    ctx = {
        'pairs':    pairs,
        'db_rates': db_rates,
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
# TRADE INQUIRY FORM & ADMIN DASHBOARD
# ════════════════════════════════════════════════════════════════════════

def trade_apply(request):
    """Public trade inquiry form — any client can submit."""
    from .models import TradeInquiry
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        inquiry = TradeInquiry.objects.create(
            full_name           = d.get('full_name','').strip(),
            company_name        = d.get('company_name','').strip(),
            business_type       = d.get('business_type','individual'),
            email               = d.get('email','').strip(),
            phone               = d.get('phone','').strip(),
            country             = d.get('country','').strip(),
            direction           = d.get('direction','import'),
            origin_country      = d.get('origin_country','').strip(),
            destination_country = d.get('destination_country','').strip(),
            coffee_type         = d.get('coffee_type','arabica'),
            quantity_kg         = float(d.get('quantity_kg', 0) or 0),
            frequency           = d.get('frequency','one_time'),
            notes               = d.get('notes','').strip(),
            casl_consent        = d.get('casl_consent') == 'on',
            user                = request.user if request.user.is_authenticated else None,
        )

        # Email Tom
        try:
            send_mail(
                subject=f'New Trade Inquiry #{inquiry.pk} — {inquiry.get_direction_display()} — {inquiry.full_name}',
                message=(
                    f'New trade inquiry received:\n\n'
                    f'Name:        {inquiry.full_name}\n'
                    f'Company:     {inquiry.company_name or "N/A"}\n'
                    f'Type:        {inquiry.get_business_type_display()}\n'
                    f'Email:       {inquiry.email}\n'
                    f'Phone:       {inquiry.phone or "N/A"}\n'
                    f'Country:     {inquiry.country}\n\n'
                    f'Direction:   {inquiry.get_direction_display()}\n'
                    f'From:        {inquiry.origin_country}\n'
                    f'To:          {inquiry.destination_country}\n'
                    f'Coffee:      {inquiry.get_coffee_type_display()}\n'
                    f'Quantity:    {inquiry.quantity_kg} kg\n'
                    f'Frequency:   {inquiry.get_frequency_display()}\n\n'
                    f'Notes:\n{inquiry.notes or "None"}\n\n'
                    f'Review at: https://tntg-corp.onrender.com/trade/dashboard/'
                ),
                from_email=getattr(djsettings,'DEFAULT_FROM_EMAIL',''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        # Confirmation to client
        try:
            send_mail(
                subject='Trade Inquiry Received — T&TG Trade Corporation',
                message=(
                    f'Dear {inquiry.full_name},\n\n'
                    f'Thank you for your trade inquiry with T&TG Trade Corporation.\n\n'
                    f'Your inquiry reference number is: #TI-{inquiry.pk:04d}\n\n'
                    f'Details submitted:\n'
                    f'  Direction:  {inquiry.get_direction_display()}\n'
                    f'  Coffee:     {inquiry.get_coffee_type_display()}\n'
                    f'  Quantity:   {inquiry.quantity_kg} kg\n'
                    f'  From:       {inquiry.origin_country}\n'
                    f'  To:         {inquiry.destination_country}\n\n'
                    f'Our team will review your inquiry and respond within 2 business days.\n\n'
                    f'T&TG Trade Corporation\n'
                    f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                    f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                ),
                from_email=getattr(djsettings,'DEFAULT_FROM_EMAIL',''),
                recipient_list=[inquiry.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request,
            f'Thank you! Your trade inquiry #TI-{inquiry.pk:04d} has been received. '
            f'We will respond within 2 business days.')
        return redirect('trade_apply')

    return render(request, 'services/trade_apply.html')


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def trade_dashboard(request):
    """Admin dashboard — manage all trade inquiries."""
    from .models import TradeInquiry

    status_filter    = request.GET.get('status', '')
    direction_filter = request.GET.get('direction', '')

    inquiries = TradeInquiry.objects.all()
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    if direction_filter:
        inquiries = inquiries.filter(direction=direction_filter)

    counts = {
        'total':     TradeInquiry.objects.count(),
        'pending':   TradeInquiry.objects.filter(status='pending').count(),
        'reviewing': TradeInquiry.objects.filter(status='reviewing').count(),
        'approved':  TradeInquiry.objects.filter(status='approved').count(),
        'rejected':  TradeInquiry.objects.filter(status='rejected').count(),
    }

    ctx = {
        'inquiries':        inquiries,
        'counts':           counts,
        'status_filter':    status_filter,
        'direction_filter': direction_filter,
    }
    return render(request, 'services/trade_dashboard.html', ctx)


@staff_member_required
def trade_update_status(request, pk):
    """Admin updates status and notes on a trade inquiry."""
    from .models import TradeInquiry
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    inquiry = get_object_or_404(TradeInquiry, pk=pk)
    if request.method == 'POST':
        new_status  = request.POST.get('status', inquiry.status)
        admin_notes = request.POST.get('admin_notes', '').strip()
        inquiry.status      = new_status
        inquiry.admin_notes = admin_notes
        inquiry.save(update_fields=['status', 'admin_notes', 'updated_at'])

        # Email client about status change
        status_messages = {
            'reviewing': 'Your trade inquiry is now under review by our team.',
            'approved':  'Your trade inquiry has been APPROVED. Our team will contact you shortly to finalise the agreement.',
            'rejected':  f'After review, we are unable to proceed with your trade inquiry at this time.\n\nReason: {admin_notes or "Please contact us for details."}',
            'completed': 'Your trade agreement has been completed successfully. Thank you for trading with T&TG!',
        }
        msg = status_messages.get(new_status)
        if msg:
            try:
                send_mail(
                    subject=f'Trade Inquiry #TI-{inquiry.pk:04d} Update — T&TG Trade Corp',
                    message=(
                        f'Dear {inquiry.full_name},\n\n{msg}\n\n'
                        f'Reference: #TI-{inquiry.pk:04d}\n\n'
                        f'T&TG Trade Corporation\n'
                        f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                        f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                    ),
                    from_email=getattr(djsettings,'DEFAULT_FROM_EMAIL',''),
                    recipient_list=[inquiry.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, f'Inquiry #TI-{pk:04d} updated to {new_status}.')
    return redirect('trade_dashboard')
