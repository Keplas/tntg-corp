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
    MONERIS_STORE_ID         — Store/Merchant ID (developer.moneris.com → Access & Credentials)
    MONERIS_API_TOKEN        — API token (developer.moneris.com → Subscriptions / API key)
    MONERIS_CHECKOUT_ID      — Checkout ID (Moneris Merchant Resource Centre → Admin → Moneris Checkout)
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
# Moneris Checkout uses store_id + api_token + checkout_id directly in the
# request body — NOT OAuth2.  OAuth2 is a separate Moneris API product.
#
# How to get each credential:
#   MONERIS_STORE_ID    → developer.moneris.com → Access & Credentials
#                         → Store/Merchant ID
#   MONERIS_API_TOKEN   → developer.moneris.com → Access & Credentials
#                         → Subscriptions (API key)
#   MONERIS_CHECKOUT_ID → Moneris Merchant Resource Centre (moneris.com login)
#                         → Admin → Moneris Checkout → generate a Checkout ID
#   MONERIS_ENVIRONMENT → 'sandbox' (default) or 'production'
MONERIS_STORE_ID      = os.environ.get('MONERIS_STORE_ID', '')
MONERIS_API_TOKEN     = os.environ.get('MONERIS_API_TOKEN', '')
MONERIS_CHECKOUT_ID   = os.environ.get('MONERIS_CHECKOUT_ID', '')
MONERIS_ENVIRONMENT   = os.environ.get('MONERIS_ENVIRONMENT', 'sandbox')

# Preload endpoint — server-to-server call that returns a ticket
_MONERIS_PRELOAD_URL = {
    'sandbox':    'https://gatewayt.moneris.com/chktv2/request/request.php',
    'production': 'https://gateway.moneris.com/chktv2/request/request.php',
}
# Hosted checkout page — buyer is redirected here with ?id=<ticket>
_MONERIS_CHECKOUT_HOST = {
    'sandbox':    'https://gatewayt.moneris.com/chkt/request/request.php',
    'production': 'https://gateway.moneris.com/chkt/request/request.php',
}


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
# MONERIS — Canadian card processing (Hosted Checkout v2)
#
# Authentication: store_id + api_token + checkout_id in the request body.
# No OAuth2 — that is a separate Moneris product.
# ════════════════════════════════════════════════════════════════════════════════

def moneris_configured():
    # Re-read from os.environ each call — avoids stale module-level values
    # if env vars were added after the first import.
    return bool(
        os.environ.get('MONERIS_STORE_ID', '').strip() and
        os.environ.get('MONERIS_API_TOKEN', '').strip() and
        os.environ.get('MONERIS_CHECKOUT_ID', '').strip()
    )


def create_moneris_checkout_session(order, success_url, cancel_url):
    """
    Create a Moneris Hosted Checkout v2 preload ticket.
    Returns (redirect_url, error).  redirect_url is None on failure.

    Buyer is redirected to:
        https://gatewayt.moneris.com/chkt/request/request.php?id=<ticket>  (sandbox)
        https://gateway.moneris.com/chkt/request/request.php?id=<ticket>   (production)
    """
    if not moneris_configured():
        return None, (
            'Moneris card payments are not yet configured. '
            'Set MONERIS_STORE_ID, MONERIS_API_TOKEN and MONERIS_CHECKOUT_ID '
            'in Cloud Run env vars.'
        )

    import logging
    logger = logging.getLogger(__name__)
    # Re-read credentials fresh — module-level vars may be stale
    store_id    = os.environ.get('MONERIS_STORE_ID', '').strip()
    api_token   = os.environ.get('MONERIS_API_TOKEN', '').strip()
    checkout_id = os.environ.get('MONERIS_CHECKOUT_ID', '').strip()
    env_setting = os.environ.get('MONERIS_ENVIRONMENT', 'sandbox').strip()
    env = env_setting if env_setting in ('sandbox', 'production') else 'sandbox'
    logger.info(f'[Moneris] config check: store_id={bool(store_id)} api_token={bool(api_token)} checkout_id={bool(checkout_id)} env={env}')

    # Moneris only processes CAD; format amount as "10.00"
    try:
        txn_total = f'{float(order.total_price):.2f}'
    except Exception:
        txn_total = str(order.total_price)

    payload = {
        'store_id':    store_id,
        'api_token':   api_token,
        'checkout_id': checkout_id,
        'txn_total':   txn_total,
        'environment': 'prod' if env == 'production' else 'qa',
        'action':      'preload',
        'order_no':    f'TNTG-{order.pk}',
        'cust_id':     order.buyer.email or str(order.buyer.pk),
        'dynamic_descriptor': f'T&TG Order #{order.pk}',
        'language':    'en',
        'return_url':  success_url,
        'cancel_url':  cancel_url,
        'bill_first_name': order.buyer.first_name or order.buyer.username,
        'bill_last_name':  order.buyer.last_name or '',
        'bill_email':      order.buyer.email or '',
    }

    try:
        resp = requests.post(
            _MONERIS_PRELOAD_URL[env],
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15,
        )
        logger.info(f'[Moneris] preload status={resp.status_code} env={env} body={resp.text[:500]}')
        if not resp.text.strip():
            return None, f'Moneris returned empty response (HTTP {resp.status_code}).'
        data = resp.json()
        # Response shape: {"response": {"success": "true", "ticket": "..."}}
        response = data.get('response', data)
        success = str(response.get('success', '')).lower()
        ticket  = response.get('ticket', '')
        if success == 'true' and ticket:
            checkout_url = f'{_MONERIS_CHECKOUT_HOST[env]}?id={ticket}'
            return checkout_url, None
        error = (response.get('error')
                 or response.get('message')
                 or f'Moneris returned: {resp.status_code} {resp.text[:200]}')
        logger.error(f'[Moneris] preload failed: {error}')
        return None, f'Moneris checkout failed: {error}'
    except Exception as e:
        logger.error(f'[Moneris] preload exception: {e}')
        return None, f'Moneris payment setup failed: {e}'


def verify_moneris_payment(ticket):
    """
    Verify a Moneris Hosted Checkout session by its ticket.
    Returns (paid: bool, reference: str).
    """
    if not moneris_configured() or not ticket:
        return False, ''

    import logging
    logger = logging.getLogger(__name__)
    store_id    = os.environ.get('MONERIS_STORE_ID', '').strip()
    api_token   = os.environ.get('MONERIS_API_TOKEN', '').strip()
    checkout_id = os.environ.get('MONERIS_CHECKOUT_ID', '').strip()
    env_setting = os.environ.get('MONERIS_ENVIRONMENT', 'sandbox').strip()
    env = env_setting if env_setting in ('sandbox', 'production') else 'sandbox'

    payload = {
        'store_id':    store_id,
        'api_token':   api_token,
        'checkout_id': checkout_id,
        'ticket':      ticket,
        'environment': 'prod' if env == 'production' else 'qa',
        'action':      'receipt',
    }
    try:
        resp = requests.post(
            _MONERIS_PRELOAD_URL[env],
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15,
        )
        data = resp.json()
        response = data.get('response', data)
        receipt  = response.get('receipt', response)
        if isinstance(receipt, dict):
            result = str(receipt.get('result', '')).lower()
            paid   = result in ('a', 'approved', '0', 'success', 'true')
            ref    = (receipt.get('referenceNum')
                      or receipt.get('txn_no')
                      or receipt.get('transaction_id')
                      or ticket)
            return paid, str(ref)
        return False, ''
    except Exception as e:
        logger.error(f'[Moneris] receipt exception: {e}')
        return False, ''
