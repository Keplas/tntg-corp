"""
T&TG Live Exchange Rates Service
Three-tier fetch chain:
  1. Frankfurter API  — free, no key, hosted by Cloudflare (primary)
  2. Open Exchange Rates — free plan, needs EXCHANGE_RATES_API_KEY on Render
  3. DB ForexRate records — last live values saved to Neon
  4. Static fallback rates — hardcoded sensible defaults
Rates cached 1 hour to stay well within free-tier limits.
"""

import requests
import logging
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

CACHE_KEY     = 'tntg_fx_rates_v3'
CACHE_TIMEOUT = 3600   # 1 hour

TARGET_CURRENCIES = ['CAD', 'UGX', 'KES', 'EUR', 'JPY']

PAIR_LABELS = {
    'CAD/UGX': ('Canadian Dollar',   'Ugandan Shilling'),
    'CAD/KES': ('Canadian Dollar',   'Kenyan Shilling'),
    'CAD/EUR': ('Canadian Dollar',   'Euro'),
    'CAD/JPY': ('Canadian Dollar',   'Japanese Yen'),
    'USD/CAD': ('US Dollar',         'Canadian Dollar'),
    'USD/UGX': ('US Dollar',         'Ugandan Shilling'),
    'USD/KES': ('US Dollar',         'Kenyan Shilling'),
    'USD/EUR': ('US Dollar',         'Euro'),
    'USD/JPY': ('US Dollar',         'Japanese Yen'),
    'EUR/UGX': ('Euro',              'Ugandan Shilling'),
    'JPY/UGX': ('Japanese Yen',      'Ugandan Shilling'),
}

# Sensible static fallback rates (USD base — updated Aug 2026)
STATIC_FALLBACK = {
    'USD': 1.0,
    'CAD': 1.36,
    'UGX': 3750.0,
    'KES': 129.0,
    'EUR': 0.92,
    'JPY': 157.0,
}


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def fetch_live_rates():
    """
    Returns dict of rates relative to USD.
    e.g. {'USD':1.0, 'CAD':1.36, 'UGX':3750, 'KES':129, 'EUR':0.92, 'JPY':157}
    """
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached

    rates = (
        _fetch_frankfurter()
        or _fetch_openexchangerates()
        or _load_from_db()
        or STATIC_FALLBACK
    )

    if rates:
        cache.set(CACHE_KEY, rates, CACHE_TIMEOUT)
        _save_to_db(rates)

    return rates


def build_pairs(rates):
    """
    Convert USD-base rates dict → list of pair dicts for templates.
    """
    if not rates:
        rates = STATIC_FALLBACK

    pairs = []

    def cross(fc, tc):
        try:
            f = Decimal(str(rates.get(fc, 1)))
            t = Decimal(str(rates.get(tc, 1)))
            if fc == 'USD':
                return t
            elif tc == 'USD':
                return Decimal('1') / f
            else:
                return t / f
        except Exception:
            return None

    for pair_key, (from_label, to_label) in PAIR_LABELS.items():
        fc, tc = pair_key.split('/')
        rate = cross(fc, tc)
        if not rate:
            continue
        pairs.append({
            'pair':       pair_key,
            'from_code':  fc,
            'to_code':    tc,
            'from_label': from_label,
            'to_label':   to_label,
            'rate':       rate,
            'display':    f'{rate:,.4f}' if rate < 10 else f'{rate:,.2f}',
        })

    return pairs


def get_rate(from_currency, to_currency):
    """Return a single cross rate as Decimal. Used by cart currency switcher."""
    rates = fetch_live_rates()
    pairs = build_pairs(rates)
    pair_key = f'{from_currency}/{to_currency}'
    for p in pairs:
        if p['pair'] == pair_key:
            return p['rate']
    # Compute directly
    try:
        f = Decimal(str(rates.get(from_currency, 1)))
        t = Decimal(str(rates.get(to_currency, 1)))
        if from_currency == 'USD':
            return t
        elif to_currency == 'USD':
            return Decimal('1') / f
        return t / f
    except Exception:
        return Decimal('1')


# ─────────────────────────────────────────────────────────────
# Tier 1: Frankfurter (free, no key)
# ─────────────────────────────────────────────────────────────

def _fetch_frankfurter():
    """
    https://api.frankfurter.app — ECB data, free, no key required.
    Base is EUR so we convert to USD base.
    """
    try:
        resp = requests.get(
            'https://api.frankfurter.app/latest',
            params={'from': 'USD', 'to': ','.join(TARGET_CURRENCIES)},
            timeout=6
        )
        data = resp.json()
        if 'rates' in data:
            rates = {'USD': 1.0}
            rates.update({k: float(v) for k, v in data['rates'].items()})
            logger.info('Frankfurter rates fetched successfully')
            return rates
    except Exception as e:
        logger.warning(f'Frankfurter API error: {e}')
    return None


# ─────────────────────────────────────────────────────────────
# Tier 2: Open Exchange Rates (needs API key)
# ─────────────────────────────────────────────────────────────

def _fetch_openexchangerates():
    api_key = getattr(settings, 'EXCHANGE_RATES_API_KEY', '').strip()
    if not api_key:
        return None
    try:
        resp = requests.get(
            'https://openexchangerates.org/api/latest.json',
            params={'app_id': api_key, 'symbols': ','.join(TARGET_CURRENCIES)},
            timeout=8
        )
        data = resp.json()
        if 'rates' in data:
            rates = {'USD': 1.0}
            rates.update({k: float(v) for k, v in data['rates'].items()})
            logger.info('OXR rates fetched successfully')
            return rates
    except Exception as e:
        logger.warning(f'OXR API error: {e}')
    return None


# ─────────────────────────────────────────────────────────────
# Tier 3: Database ForexRate records
# ─────────────────────────────────────────────────────────────

def _save_to_db(rates):
    try:
        from services.models import ForexRate
        usd_to = lambda c: Decimal(str(rates.get(c, 1)))
        pairs_to_save = [
            ('CAD', 'UGX', usd_to('UGX') / usd_to('CAD')),
            ('CAD', 'KES', usd_to('KES') / usd_to('CAD')),
            ('USD', 'CAD', usd_to('CAD')),
            ('USD', 'UGX', usd_to('UGX')),
            ('USD', 'KES', usd_to('KES')),
            ('EUR', 'UGX', usd_to('UGX') / usd_to('EUR')),
            ('JPY', 'UGX', usd_to('UGX') / usd_to('JPY')),
        ]
        for fc, tc, rate in pairs_to_save:
            ForexRate.objects.update_or_create(
                from_currency=fc, to_currency=tc,
                defaults={'rate': rate}
            )
    except Exception as e:
        logger.warning(f'Could not save rates to DB: {e}')


def _load_from_db():
    try:
        from services.models import ForexRate
        db_rates = list(ForexRate.objects.all())
        if not db_rates:
            return None
        rates = {'USD': 1.0}
        for r in db_rates:
            if r.from_currency == 'USD':
                rates[r.to_currency] = float(r.rate)
        if len(rates) > 2:
            logger.info('Loaded rates from DB fallback')
            return rates
    except Exception as e:
        logger.warning(f'DB rates load error: {e}')
    return None
