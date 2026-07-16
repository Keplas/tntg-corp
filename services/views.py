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
