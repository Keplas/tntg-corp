"""
Email notifications — order confirmations, loyalty point credits, shipping
updates.

SAFE-BY-DEFAULT: if SMTP credentials aren't set via environment variables,
emails are printed to the console/server logs instead of actually being
sent — so nothing crashes and you can see exactly what *would* have been
sent while testing.

Required environment variables for real email delivery (set on Render,
never commit these):
    EMAIL_HOST            — e.g. smtp.gmail.com, or your SendGrid/Mailgun host
    EMAIL_PORT            — usually 587
    EMAIL_HOST_USER        — your SMTP username / API key ID
    EMAIL_HOST_PASSWORD    — your SMTP password / API key secret
    EMAIL_USE_TLS          — "True" or "False" (default True)
    DEFAULT_FROM_EMAIL     — e.g. "T&TG Trade Corp <no-reply@tntgcorp.com>"

Works with Gmail SMTP, SendGrid, Mailgun, or any standard SMTP provider —
just supply the right host/port/credentials for whichever you choose.
"""
import os
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.utils.html import strip_tags

EMAIL_HOST          = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587') or 587)
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'T&TG Trade Corp <no-reply@tntgcorp.com>')


def email_configured():
    return bool(EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)


def _get_backend():
    if email_configured():
        return EmailBackend(
            host=EMAIL_HOST, port=EMAIL_PORT,
            username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD,
            use_tls=EMAIL_USE_TLS, fail_silently=True,
        )
    return ConsoleBackend(fail_silently=True)


def _send(subject, html_body, to_email):
    if not to_email:
        return False
    try:
        backend = _get_backend()
        msg = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),
            from_email=DEFAULT_FROM_EMAIL,
            to=[to_email],
            connection=backend,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
        return True
    except Exception:
        return False


# ── Branded HTML wrapper ─────────────────────────────────────────────
def _wrap(title, body_html, cta_text=None, cta_url=None):
    cta_html = ''
    if cta_text and cta_url:
        cta_html = f'''
        <tr><td style="padding:24px 0 8px;text-align:center">
          <a href="{cta_url}" style="display:inline-block;padding:13px 28px;
             background:linear-gradient(135deg,#c9a84c,#e8c96a);color:#060f1e;
             font-weight:800;text-decoration:none;border-radius:8px;font-size:14px">
            {cta_text}
          </a>
        </td></tr>'''
    return f'''
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#060f1e;padding:40px 0;font-family:Arial,sans-serif">
      <tr><td align="center">
        <table width="540" cellpadding="0" cellspacing="0" style="background:#0d1f35;border-radius:16px;overflow:hidden;border:1px solid rgba(201,168,76,.2)">
          <tr><td style="background:linear-gradient(135deg,#0a1830,#0d1f35);padding:28px 32px;border-bottom:1px solid rgba(201,168,76,.2)">
            <span style="color:#fff;font-size:18px;font-weight:900">T&amp;TG <span style="color:#c9a84c">Trade Corp</span></span>
          </td></tr>
          <tr><td style="padding:32px">
            <h2 style="color:#fff;font-size:20px;margin:0 0 16px">{title}</h2>
            <div style="color:#c4cdd6;font-size:14px;line-height:1.7">{body_html}</div>
          </td></tr>
          {cta_html}
          <tr><td style="padding:20px 32px;border-top:1px solid rgba(201,168,76,.12);text-align:center">
            <span style="color:#6a88a8;font-size:11px">T&amp;TG Trade Corporation · Canada · Uganda · Kenya</span>
          </td></tr>
        </table>
      </td></tr>
    </table>'''


# ── Transactional emails ─────────────────────────────────────────────

def send_order_placed_email(order):
    body = f'''
      <p>Hi {order.buyer.get_short_name() or order.buyer.username},</p>
      <p>We've received your order. Here's a summary:</p>
      <p>
        <strong>Order #{order.pk}</strong><br>
        Product: {order.product.name}<br>
        Quantity: {order.quantity}<br>
        Total: ${order.total_price}<br>
        Delivery to: {order.destination_country}
      </p>
      <p>You'll receive another email once payment is confirmed and again when your order ships.</p>
    '''
    html = _wrap('Order Received', body)
    return _send(f'Order #{order.pk} Received — T&TG Trade Corp', html, order.buyer.email)


def send_order_confirmation_email(order):
    body = f'''
      <p>Hi {order.buyer.get_short_name() or order.buyer.username},</p>
      <p>Payment confirmed for <strong>Order #{order.pk}</strong> — {order.product.name}.</p>
      <p>
        Amount paid: <strong>${order.total_price}</strong><br>
        Loyalty points earned: <strong style="color:#c9a84c">{order.avon_points_earned}</strong><br>
        Reward payout date: {order.reward_payment_date.strftime('%d %b %Y') if order.reward_payment_date else '—'}
      </p>
      <p>We'll notify you again as soon as your order ships.</p>
    '''
    html = _wrap('Payment Confirmed', body)
    return _send(f'Payment Confirmed — Order #{order.pk}', html, order.buyer.email)


def send_shipping_update_email(order):
    status_labels = {
        'processing': 'is being processed',
        'accepted':   'has been accepted',
        'shipped':    'has shipped',
        'delivered':  'has been delivered',
    }
    status_text = status_labels.get(order.status, f'status changed to {order.get_status_display()}')
    body = f'''
      <p>Hi {order.buyer.get_short_name() or order.buyer.username},</p>
      <p>Your order <strong>#{order.pk}</strong> — {order.product.name} — {status_text}.</p>
    '''
    html = _wrap('Order Update', body, cta_text='View Order', cta_url=f'https://tntgcorp.com/marketplace/orders/{order.pk}/')
    return _send(f'Order #{order.pk} Update — T&TG Trade Corp', html, order.buyer.email)


def send_loyalty_points_credited_email(user, points, description=''):
    body = f'''
      <p>Hi {user.get_short_name() or user.username},</p>
      <p>You just earned <strong style="color:#c9a84c">{points} T&amp;TG Loyalty Points</strong>!</p>
      <p>{description}</p>
      <p>Your total balance: <strong>{user.avon_points}</strong> points.</p>
    '''
    html = _wrap('Loyalty Points Credited', body, cta_text='View My Points', cta_url='https://tntgcorp.com/accounts/loyalty/')
    return _send('Loyalty Points Credited — T&TG Trade Corp', html, user.email)
