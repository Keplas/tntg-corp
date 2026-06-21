"""
Payment integration — Stripe (cards, Canada) + Flutterwave (mobile money,
Uganda/Kenya: MTN, Airtel, M-Pesa).

SAFE-BY-DEFAULT: if API keys aren't configured (via environment variables),
these functions return a clear "not configured" result instead of crashing
or silently failing — so the rest of the checkout flow degrades gracefully
until real credentials are added.

Required environment variables (set these on Render, never commit them):
    STRIPE_SECRET_KEY          — starts with sk_test_... or sk_live_...
    STRIPE_PUBLISHABLE_KEY     — starts with pk_test_... or pk_live_...
    STRIPE_WEBHOOK_SECRET      — starts with whsec_...
    FLUTTERWAVE_CLIENT_ID      — UUID, from Flutterwave sandbox/live dashboard
    FLUTTERWAVE_CLIENT_SECRET  — from the same dashboard page

Note on Flutterwave: this targets the v4 API, which uses OAuth2
(Client ID/Secret exchanged for a short-lived access token) rather than a
static secret key — this is what Flutterwave's sandbox issues by default
for new developer accounts as of mid-2026. v4 is public beta; if Flutterwave
changes endpoint behaviour, the create/verify functions below are the
isolated place to update.

IMPORTANT — mobile money UX difference from card payments: unlike Stripe's
hosted checkout (which redirects to a payment page), Flutterwave v4 mobile
money sends a PUSH NOTIFICATION directly to the customer's phone. There is
no redirect link — the customer must open that notification and approve on
their device, then your app polls/checks the charge status. See
payment_pending.html / the poll_payment_status view for how this is handled.
"""
import os
import time
import requests
from decimal import Decimal

STRIPE_SECRET_KEY      = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET   = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

FLUTTERWAVE_CLIENT_ID     = os.environ.get('FLUTTERWAVE_CLIENT_ID', '')
FLUTTERWAVE_CLIENT_SECRET = os.environ.get('FLUTTERWAVE_CLIENT_SECRET', '')

# Sandbox base URL. Flutterwave's "Go Live" step issues a separate
# production base URL — update this (or make it env-driven) when you
# switch from sandbox to live credentials.
FLUTTERWAVE_API_BASE  = 'https://developersandbox-api.flutterwave.com'
FLUTTERWAVE_TOKEN_URL = 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token'

# Simple in-process token cache — avoids re-authenticating on every request.
# Lives only as long as the worker process; fine at this order volume.
_flw_token_cache = {'token': None, 'expires_at': 0}


def stripe_configured():
    return bool(STRIPE_SECRET_KEY)


def flutterwave_configured():
    return bool(FLUTTERWAVE_CLIENT_ID and FLUTTERWAVE_CLIENT_SECRET)


# ── Stripe (cards) ───────────────────────────────────────────────────

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


# ── Flutterwave v4 (mobile money) ────────────────────────────────────

def _get_flutterwave_token():
    """Fetches (and caches) an OAuth2 access token via client_credentials grant."""
    now = time.time()
    if _flw_token_cache['token'] and _flw_token_cache['expires_at'] > now + 30:
        return _flw_token_cache['token']
    try:
        resp = requests.post(FLUTTERWAVE_TOKEN_URL, data={
            'client_id': FLUTTERWAVE_CLIENT_ID,
            'client_secret': FLUTTERWAVE_CLIENT_SECRET,
            'grant_type': 'client_credentials',
        }, timeout=15)
        data = resp.json()
        token = data.get('access_token')
        if not token:
            return None
        _flw_token_cache['token'] = token
        _flw_token_cache['expires_at'] = now + int(data.get('expires_in', 600))
        return token
    except Exception:
        return None


def convert_currency(amount, from_currency, to_currency):
    """
    Converts `amount` from `from_currency` to `to_currency` using the
    ForexRate table (Services app — admin-editable at /admin or via the
    Services > Forex Rates page).

    Returns (converted_amount: Decimal|None, error: str|None). Deliberately
    does NOT fall back to a guessed/default rate if one isn't found —
    charging the wrong amount of real money is worse than blocking the
    payment with a clear error.
    """
    if from_currency == to_currency:
        return amount, None
    from services.models import ForexRate
    try:
        rate_obj = ForexRate.objects.get(from_currency=from_currency, to_currency=to_currency)
        return amount * rate_obj.rate, None
    except ForexRate.DoesNotExist:
        return None, (
            f'No exchange rate is configured for {from_currency}/{to_currency}. '
            f'Please contact support, or an admin can add this rate under Forex Rates.'
        )


def create_flutterwave_payment(order, customer_phone, local_amount, country_code='256', network='MTN', currency='UGX'):
    """
    Initiates a mobile money charge via Flutterwave's v4 orchestrator
    endpoint (single call — creates the customer, payment method, and
    charge together).

    IMPORTANT: `local_amount` must already be converted into `currency`
    by the caller (see convert_currency() above) — this function does NOT
    convert order.total_price itself, since silently treating a USD total
    as a UGX/KES amount was the exact bug that caused wildly wrong charges.

    Unlike Stripe, there's no redirect link: the customer gets a push
    notification on their phone and must approve there. Returns
    (charge_id, instruction_note, error) — charge_id is used later to
    poll/verify status; instruction_note is the customer-facing text
    Flutterwave returns describing how to complete the payment (this is
    the ONLY way to see what to do in sandbox mode, since no real push
    notification is sent to a real phone there).
    """
    if not flutterwave_configured():
        return None, None, 'Mobile Money payments are not yet configured. Please contact support or choose Card.'

    token = _get_flutterwave_token()
    if not token:
        return None, None, 'Could not authenticate with the Mobile Money provider. Please try again shortly.'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Trace-Id': f'tntg-order-{order.pk}-{int(time.time())}',
        'X-Idempotency-Key': f'tntg-order-{order.pk}-{int(time.time())}',
    }
    first_name = order.buyer.first_name or order.buyer.username
    last_name  = order.buyer.last_name or ''

    payload = {
        'amount': float(local_amount),
        'currency': currency,
        'reference': f'TNTG-ORDER-{order.pk}-{int(time.time())}',
        'payment_method': {
            'type': 'mobile_money',
            'mobile_money': {
                'country_code': country_code,
                'network': network,
                'phone_number': customer_phone,
            },
        },
        'customer': {
            'email': order.buyer.email or 'no-reply@tntgcorp.com',
            'name': {'first': first_name, 'last': last_name},
            'phone': {'country_code': country_code, 'number': customer_phone},
        },
    }

    try:
        resp = requests.post(f'{FLUTTERWAVE_API_BASE}/orchestration/direct-charges',
                              json=payload, headers=headers, timeout=20)
        data = (resp.json().get('data') or {})
        charge_id = data.get('id')
        if not charge_id:
            return None, None, resp.json().get('message', 'Payment initiation failed. Please check the phone number and try again.')

        # Extract the customer-facing instruction text — in sandbox this is
        # the ONLY way to see what to do next (no real push notification is
        # sent to a real phone in test mode). In live mode, this is the same
        # text that accompanies the real push notification.
        next_action = data.get('next_action') or {}
        instruction_note = (
            (next_action.get('payment_instruction') or {}).get('note')
            or (next_action.get('payment_instruction') or {}).get('message')
            or None
        )
        return str(charge_id), instruction_note, None
    except Exception as e:
        return None, None, f'Payment setup failed: {e}'


def verify_flutterwave_transaction(charge_id):
    """
    Checks a Flutterwave v4 charge's status by ID.
    Returns (paid: bool, reference: str, raw_status: str).
    Defensive about exact field naming since v4 is in public beta —
    treats any status containing "success" (case-insensitive) as paid.
    """
    if not flutterwave_configured() or not charge_id:
        return False, '', ''

    token = _get_flutterwave_token()
    if not token:
        return False, '', ''

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    try:
        resp = requests.get(f'{FLUTTERWAVE_API_BASE}/charges/{charge_id}', headers=headers, timeout=15)
        data = (resp.json().get('data') or {})
        status = str(data.get('status', '')).lower()
        paid = 'success' in status or status == 'completed'
        return paid, str(data.get('id', charge_id)), status
    except Exception:
        return False, '', ''
