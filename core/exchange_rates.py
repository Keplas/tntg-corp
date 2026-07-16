"""
T&TG Live Exchange Rates Service
─────────────────────────────────
Fetches rates from Open Exchange Rates API, caches for 1 hour,
and saves to ForexRate DB records as a fallback.

Set EXCHANGE_RATES_API_KEY on Render to activate.
Free plan: 1,000 req/month — with 1-hr cache we use ~24/day = ~720/month.
"""

import requests
import logging
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Pairs T&TG cares about (USD is OXR base, so we calculate cross-rates)
TARGET_CURRENCIES = ['CAD', 'UGX', 'KES', 'USD']

PAIR_LABELS = {
    'CAD/UGX': ('Canadian Dollar', 'Ugandan Shilling'),
    'CAD/KES': ('Canadian Dollar', 'Kenyan Shilling'),
    'USD/CAD': ('US Dollar',       'Canadian Dollar'),
    'USD/UGX': ('US Dollar',       'Ugandan Shilling'),
    'USD/KES': ('US Dollar',       'Kenyan Shilling'),
    'UGX/KES': ('Ugandan Shilling','Kenyan Shilling'),
}

CACHE_KEY = 'oxr_rates_v2'


def fetch_live_rates():
    """
    Returns dict of rates relative to USD, e.g. {'CAD': 1.36, 'UGX': 3750, ...}
    Uses cache first. Falls back to DB ForexRate records if API unavailable.
    """
    # 1. Try cache
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached

    api_key = getattr(settings, 'EXCHANGE_RATES_API_KEY', '')

    # 2. Try Open Exchange Rates API
    if api_key:
        try:
            resp = requests.get(
                'https://openexchangerates.org/api/latest.json',
                params={
                    'app_id': api_key,
                    'symbols': ','.join(TARGET_CURRENCIES),
                },
                timeout=8
            )
            data = resp.json()
            if 'rates' in data:
                rates = data['rates']
                cache.set(CACHE_KEY, rates, 3600)  # cache 1 hour
                _save_to_db(rates)
                logger.info('OXR rates refreshed successfully')
                return rates
        except Exception as e:
            logger.warning(f'OXR API error: {e}')

    # 3. Fallback — load from DB
    return _load_from_db()


def build_pairs(rates):
    """
    Convert USD-based rates dict to a list of cross-rate pair dicts
    ready to pass to templates.
    """
    if not rates:
        return []

    pairs = []
    usd_to = lambda c: Decimal(str(rates.get(c, 1)))

    def cross(from_c, to_c):
        """Calculate from_c → to_c cross rate via USD."""
        try:
            if from_c == 'USD':
                return usd_to(to_c)
            elif to_c == 'USD':
                return Decimal('1') / usd_to(from_c)
            else:
                return usd_to(to_c) / usd_to(from_c)
        except Exception:
            return None

    for pair_key, (from_label, to_label) in PAIR_LABELS.items():
        fc, tc = pair_key.split('/')
        rate = cross(fc, tc)
        if rate:
            pairs.append({
                'pair':       pair_key,
                'from_code':  fc,
                'to_code':    tc,
                'from_label': from_label,
                'to_label':   to_label,
                'rate':       rate,
                'display':    f'{rate:,.4f}' if rate < 100 else f'{rate:,.2f}',
            })

    return pairs


def _save_to_db(rates):
    """Persist latest rates to ForexRate model as backup."""
    try:
        from services.models import ForexRate
        usd_to = lambda c: Decimal(str(rates.get(c, 1)))

        pairs_to_save = [
            ('CAD', 'UGX', usd_to('UGX') / usd_to('CAD')),
            ('CAD', 'KES', usd_to('KES') / usd_to('CAD')),
            ('USD', 'CAD', usd_to('CAD')),
            ('USD', 'UGX', usd_to('UGX')),
            ('USD', 'KES', usd_to('KES')),
            ('UGX', 'KES', usd_to('KES') / usd_to('UGX')),
        ]
        for fc, tc, rate in pairs_to_save:
            ForexRate.objects.update_or_create(
                from_currency=fc, to_currency=tc,
                defaults={'rate': rate}
            )
    except Exception as e:
        logger.warning(f'Could not save rates to DB: {e}')


def _load_from_db():
    """Load rates from DB ForexRate records (fallback)."""
    try:
        from services.models import ForexRate
        db_rates = ForexRate.objects.all()
        # Reconstruct approximate USD-base rates from DB pairs
        rates = {'USD': 1.0}
        for r in db_rates:
            if r.from_currency == 'USD':
                rates[r.to_currency] = float(r.rate)
            elif r.to_currency == 'USD':
                rates[r.from_currency] = 1.0 / float(r.rate)
        return rates if len(rates) > 1 else None
    except Exception:
        return None
