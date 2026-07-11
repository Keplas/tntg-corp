"""
Payment integration — Stripe (cards, Canada) + Flutterwave (mobile money,
Uganda/Kenya: MTN, Airtel, M-Pesa).

SAFE-BY-DEFAULT: if API keys aren't configured (via environment variables),
these functions return a clear "not configured" result instead of crashing
or silently failing — so the rest of the checkout flow degrades gracefully
until real credentials are added.

Required environment variables (set these on Render, never commit them):
    STRIPE_SECRET_KEY        — starts with sk_test_... or sk_live_...
    STRIPE_PUBLISHABLE_KEY   — starts with pk_test_... or pk_live_...
    STRIPE_WEBHOOK_SECRET    — starts with whsec_...
    FLUTTERWAVE_SECRET_KEY   — starts with FLWSECK_TEST-... or FLWSECK-...
    FLUTTERWAVE_PUBLIC_KEY   — starts with FLWPUBK_TEST-... or FLWPUBK-...
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
