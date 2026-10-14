"""
Payment integration — Stripe (cards, Canada) + Flutterwave (mobile money,
Uganda/Kenya: MTN, Airtel, M-Pesa) + Moneris (Canadian card payments).

SAFE-BY-DEFAULT: if API keys aren't configured (via environment variables),
these functions return a clear "not configured" result instead of crashing
or silently failing — so the rest of the checkout flow degrades gracefully
until real credentials are added.

Required environment variables (set these on Render/Cloud Run, never commit them):
    STRIPE_SECRET_KEY        — starts with sk_test_... or sk_live_...
    STRIPE_PUBLISHABLE_KEY   — starts with pk_test_... or pk_live_...
    STRIPE_WEBHOOK_SECRET    — starts with whsec_...
    FLUTTERWAVE_SECRET_KEY   — starts with FLWSECK_TEST-... or FLWSECK-...
    FLUTTERWAVE_PUBLIC_KEY   — starts with FLWPUBK_TEST-... or FLWPUBK-...
    MONERIS_CLIENT_ID        — OAuth2 client ID from Moneris developer portal
    MONERIS_CLIENT_SECRET    — OAuth2 client secret from Moneris developer portal
    MONERIS_ENVIRONMENT      — 'sandbox' (default) or 'production'
"""
import os
import requests
from decimal import Decimal

STRIPE_SECRET_KEY      = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET   = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

FLUTTERWAVE_SECRET_KEY = os.environ.get('FLUTTERWAVE_SECRET_KEY', '')
FLUTTERWAVE_PUBLIC_KEY = os.environ.get('FLUTTERWAVE_PUBLIC_KEY', '')

FLUTTERWAVE_API_BASE = 'https://api.flutterwave.com/v3'

# ── Moneris ───────────────────────────────────────────────────────────────────
MONERIS_CLIENT_ID     = os.environ.get('MONERIS_CLIENT_ID', '')
MONERIS_CLIENT_SECRET = os.environ.get('MONERIS_CLIENT_SECRET', '')
MONERIS_ENVIRONMENT   = os.environ.get('MONERIS_ENVIRONMENT', 'sandbox')  # 'sandbox' or 'production'

_MONERIS_TOKEN_URL = {
    'sandbox':    'https://api.sb.moneris.io/oauth2/token',
    'production': 'https://api.moneris.io/oauth2/token',
}
_MONERIS_API_BASE = {
    'sandbox':    'https://api.sb.moneris.io',
    'production': 'https://api.moneris.io',
}
# Hosted checkout redirect base (buyer is sent here with ?id=<ticket>)
_MONERIS_CHECKOUT_HOST = {
    'sandbox':    'https://gatewayt.moneris.com/chkt/request/request.php',
    'production': 'https://gateway.moneris.com/chkt/request/request.php',
}

# In-process token cache so we don't re-fetch for every request
_moneris_token_cache = {'token': '', 'expires_at': 0}


def stripe_configured():
    return bool(STRIPE_SECRET_KEY)


def flutterwave_configured():
    return bool(FLUTTERWAVE_SECRET_KEY)


def create_stripe_checkout_session(order, success_url, cancel_url):
    """
    Creates a Stripe Checkout session for a card payment.
    Returns (session_url, error). On misconfiguration, session_url is None
    and error contains a human-readable message.
    """
    if not stripe_configured():
        return None, 'Card payments are not yet configured. Please contact support or choose Mobile Money.'

    import stripe
    stripe.api_key = STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"{order.product.name} (x{order.quantity})"},
                    'unit_amount': int((order.total_price / order.quantity) * 100),
                },
                'quantity': order.quantity,
            }],
            customer_email=order.buyer.email or None,
            client_reference_id=str(order.pk),
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={'order_id': str(order.pk)},
        )
        return session.url, None
    except Exception as e:
        return None, f'Payment setup failed: {e}'


def verify_stripe_session(session_id):
    """Verify a completed Stripe session. Returns (paid: bool, reference: str)."""
    if not stripe_configured():
        return False, ''
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == 'paid', session.id
    except Exception:
        return False, ''


def create_flutterwave_payment(order, redirect_url, customer_phone=''):
    """
    Initiates a Flutterwave payment (supports MTN/Airtel Money, M-Pesa, cards).
    Returns (payment_link, error).
    """
    if not flutterwave_configured():
        return None, 'Mobile Money payments are not yet configured. Please contact support or choose Card.'

    headers = {
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'tx_ref': f'TNTG-ORDER-{order.pk}-{order.created_at.timestamp():.0f}',
        'amount': str(order.total_price),
        'currency': 'USD',
        'redirect_url': redirect_url,
        'customer': {
            'email': order.buyer.email or 'no-reply@tntgcorp.com',
            'phonenumber': customer_phone,
            'name': order.buyer.get_full_name() or order.buyer.username,
        },
        'customizations': {
            'title': 'T&TG Trade Corp',
            'description': f'Order #{order.pk} — {order.product.name}',
        },
        'meta': {'order_id': str(order.pk)},
    }

    try:
        resp = requests.post(f'{FLUTTERWAVE_API_BASE}/payments', json=payload, headers=headers, timeout=15)
        data = resp.json()
        if data.get('status') == 'success':
            return data['data']['link'], None
        return None, data.get('message', 'Payment initiation failed.')
    except Exception as e:
        return None, f'Payment setup failed: {e}'


def verify_flutterwave_transaction(transaction_id):
    """Verify a Flutterwave transaction by its ID. Returns (paid: bool, reference: str)."""
    if not flutterwave_configured():
        return False, ''
    headers = {'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}'}
    try:
        resp = requests.get(f'{FLUTTERWAVE_API_BASE}/transactions/{transaction_id}/verify',
                             headers=headers, timeout=15)
        data = resp.json()
        if data.get('status') == 'success' and data['data']['status'] == 'successful':
            return True, str(data['data']['id'])
        return False, ''
    except Exception:
        return False, ''


# ════════════════════════════════════════════════════════════════════════════════
# MONERIS — Canadian card processing (OAuth 2.0 + Hosted Checkout)
# ════════════════════════════════════════════════════════════════════════════════

def moneris_configured():
    return bool(MONERIS_CLIENT_ID and MONERIS_CLIENT_SECRET)


def _get_moneris_token():
    """
    Fetch a Moneris OAuth2 access token using client_credentials.
    Caches the token in-process until 60 seconds before expiry.
    """
    import time
    now = time.time()
    if _moneris_token_cache['token'] and now < _moneris_token_cache['expires_at']:
        return _moneris_token_cache['token']

    env = MONERIS_ENVIRONMENT if MONERIS_ENVIRONMENT in ('sandbox', 'production') else 'sandbox'
    resp = requests.post(
        _MONERIS_TOKEN_URL[env],
        data={
            'grant_type':    'client_credentials',
            'client_id':     MONERIS_CLIENT_ID,
            'client_secret': MONERIS_CLIENT_SECRET,
            'scope':         'payment.write',
        },
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()
    token = body['access_token']
    expires_in = int(body.get('expires_in', 3600))
    _moneris_token_cache['token'] = token
    _moneris_token_cache['expires_at'] = now + expires_in - 60  # 60 s safety margin
    return token


def create_moneris_checkout_session(order, success_url, cancel_url):
    """
    Create a Moneris hosted-checkout session.
    Returns (redirect_url, error).  On misconfiguration redirect_url is None.

    The checkout page URL takes the form:
        https://gatewayt.moneris.com/chkt/request/request.php?id=<ticket>  (sandbox)
        https://gateway.moneris.com/chkt/request/request.php?id=<ticket>   (production)
    """
    if not moneris_configured():
        return None, ('Moneris card payments are not yet configured. '
                      'Please choose Mobile Money or Bank Transfer.')
    env = MONERIS_ENVIRONMENT if MONERIS_ENVIRONMENT in ('sandbox', 'production') else 'sandbox'
    try:
        token = _get_moneris_token()
    except Exception as e:
        return None, f'Moneris authentication failed: {e}'

    currency = (order.display_currency or 'CAD').upper()
    # Moneris only processes CAD and USD natively; fall back to CAD for others
    if currency not in ('CAD', 'USD'):
        currency = 'CAD'

    amount = str(
        order.display_total if order.display_currency == currency else order.total_price
    )

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type':  'application/json',
    }
    payload = {
        'amount':       amount,
        'currency':     currency,
        'order_id':     f'TNTG-{order.pk}',
        'redirect_url': success_url,
        'cancel_url':   cancel_url,
        'billing': {
            'email':      order.buyer.email or '',
            'first_name': order.buyer.first_name or order.buyer.username,
            'last_name':  order.buyer.last_name or '',
        },
        'description': f'T&TG Order #{order.pk} — {order.product.name} x{order.quantity}',
    }

    try:
        resp = requests.post(
            f'{_MONERIS_API_BASE[env]}/checkout/v1/session',
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = resp.json()
        # The ticket may be at top-level or nested under 'data'
        ticket = (data.get('ticket')
                  or data.get('data', {}).get('ticket')
                  or data.get('response', {}).get('ticket'))
        if not ticket:
            msg = (data.get('message')
                   or data.get('error')
                   or data.get('data', {}).get('message')
                   or f'Moneris returned: {resp.status_code}')
            return None, f'Moneris checkout failed: {msg}'
        checkout_url = f'{_MONERIS_CHECKOUT_HOST[env]}?id={ticket}'
        return checkout_url, None
    except Exception as e:
        return None, f'Moneris payment setup failed: {e}'


def verify_moneris_payment(ticket):
    """
    Verify a Moneris hosted-checkout session by its ticket.
    Returns (paid: bool, reference: str).
    """
    if not moneris_configured() or not ticket:
        return False, ''
    env = MONERIS_ENVIRONMENT if MONERIS_ENVIRONMENT in ('sandbox', 'production') else 'sandbox'
    try:
        token = _get_moneris_token()
    except Exception:
        return False, ''

    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(
            f'{_MONERIS_API_BASE[env]}/checkout/v1/receipt/{ticket}',
            headers=headers,
            timeout=15,
        )
        data = resp.json()
        # Receipt may be at top-level or nested under 'data' / 'receipt'
        receipt = (data.get('receipt')
                   or data.get('data', {}).get('receipt')
                   or data)
        if isinstance(receipt, dict):
            result = str(receipt.get('result', '')).lower()
            paid   = result in ('a', 'approved', '0', 'success', 'true')
            ref    = (receipt.get('referenceNum')
                      or receipt.get('txn_no')
                      or receipt.get('transaction_id')
                      or ticket)
            return paid, str(ref)
        return False, ''
    except Exception:
        return False, ''
