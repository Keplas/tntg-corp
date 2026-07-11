from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, date
from .models import Product, Order, ProductReview
from accounts.models import AvonPointTransaction
from core.models import Notification, LoyaltySettings
from core.emails import send_order_placed_email, send_order_confirmation_email
from . import payments
import decimal


def product_list(request):
    # Capture referral code from a shared link (?ref=UNIQUE_ID) into the session
    # so it survives browsing and auto-fills at checkout, without requiring
    # the new buyer to manually type the referrer's ID.
    ref_code = request.GET.get('ref', '')
    if ref_code:
        request.session['referred_by'] = ref_code
        request.session.set_expiry(60 * 60 * 24 * 14)  # remember for 14 days

    market   = request.GET.get('market', 'both')
    category = request.GET.get('category', '')
    gender   = request.GET.get('gender', '')
    query    = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    if market in ['local', 'international']:
        products = products.filter(market_type__in=[market, 'both'])
    if category:
        products = products.filter(category=category)
    if gender:
        products = products.filter(gender_target__in=[gender, 'all'])
    if query:
        products = products.filter(name__icontains=query)
    ctx = {
        'products': products,
        'market':   market,
        'category': category,
        'gender':   gender,
        'query':    query,
        'categories': Product._meta.get_field('category').choices,
        'genders':    Product._meta.get_field('gender_target').choices,
    }
    return render(request, 'marketplace/product_list.html', ctx)


def product_detail(request, pk):
    ref_code = request.GET.get('ref', '')
    if ref_code:
        request.session['referred_by'] = ref_code
        request.session.set_expiry(60 * 60 * 24 * 14)

    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.all()[:10]
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    ctx = {'product': product, 'reviews': reviews, 'related': related}
    return render(request, 'marketplace/product_detail.html', ctx)


@login_required
def place_order(request, pk):
    product  = get_object_or_404(Product, pk=pk, is_active=True)
    settings = LoyaltySettings.get_settings()
    session_referral = request.session.get('referred_by', '')

    if request.method == 'POST':
        qty          = int(request.POST.get('quantity', 1))
        delivery     = request.POST.get('delivery_type', 'ordinary')
        dest_country = request.POST.get('destination_country', '')
        dest_address = request.POST.get('destination_address', '')
        arrival_date = request.POST.get('desired_arrival_date', '')
        arrival_time = request.POST.get('desired_arrival_time', '') or None
        referred_by  = request.POST.get('referred_by', '') or session_referral
        referrer_id  = request.POST.get('referrer_unique_id', '') or session_referral

        total = product.price * qty

        # Use LoyaltySettings rates (1% consumer / 2.5% referral)
        if referred_by:
            rate = decimal.Decimal(str(settings.referral_rate))
            tx_type = 'earn_referral'
        else:
            rate = decimal.Decimal(str(settings.consumer_rate))
            tx_type = 'earn_purchase'

        pts = (total * rate).quantize(decimal.Decimal('0.01'))

        # Reward payment is due on the Nth day after purchase (default 45)
        reward_date = date.today() + timedelta(days=settings.payment_days)

        order = Order.objects.create(
            buyer               = request.user,
            product             = product,
            order_type          = 'buy',
            quantity            = qty,
            total_price         = total,
            delivery_type       = delivery,
            destination_country = dest_country,
            destination_address = dest_address,
            desired_arrival_date= arrival_date,
            desired_arrival_time= arrival_time,
            referred_by         = referred_by,
            referrer_unique_id  = referrer_id,
            avon_points_earned  = pts,
            reward_payment_date = reward_date,
        )

        request.user.avon_points += pts
        request.user.save()

        AvonPointTransaction.objects.create(
            user             = request.user,
            transaction_type = tx_type,
            points           = pts,
            description      = f"Earned from Order #{order.pk}: {product.name}",
            status           = 'completed',
            min_execution_date = reward_date,
        )

        Notification.notify(
            'order_placed',
            f"New Order #{order.pk} — {product.name}",
            (
                f"Buyer: {request.user.get_full_name() or request.user.username} "
                f"({request.user.unique_id}) | Qty: {qty} | Total: ${total} | "
                f"Delivery to: {dest_country} | Loyalty Points: {pts} | "
                f"Reward due: {reward_date}"
            ),
            f'/admin/marketplace/order/{order.pk}/change/'
        )

        send_order_placed_email(order)

        rate_pct = float(rate) * 100
        messages.success(
            request,
            f'Order placed! You earned {pts} T&TG Loyalty Points '
            f'({rate_pct:.1f}% of ${total}). '
            f'Reward payment scheduled for {reward_date.strftime("%d %b %Y")}.'
        )
        return redirect('payment_select', pk=order.pk)

    return render(request, 'marketplace/place_order.html', {
        'product':  product,
        'settings': settings,
        'session_referral': session_referral,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'marketplace/order_detail.html', {'order': order})


def market_select(request):
    return render(request, 'marketplace/market_select.html')


# ═══════════════════════════════════════════════════════════════
# PAYMENTS — card (Stripe) and mobile money (Flutterwave)
# ═══════════════════════════════════════════════════════════════

@login_required
def payment_select(request, pk):
    """Let the buyer choose a payment method, or pay later (cash/manual)."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'marketplace/payment_select.html', {
        'order': order,
        'stripe_ready': payments.stripe_configured(),
        'flutterwave_ready': payments.flutterwave_configured(),
    })


@login_required
def payment_start_card(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    success_url = request.build_absolute_uri(reverse('payment_success', args=[order.pk]))
    cancel_url  = request.build_absolute_uri(reverse('payment_select', args=[order.pk]))

    session_url, error = payments.create_stripe_checkout_session(order, success_url, cancel_url)
    if error:
        messages.error(request, error)
        return redirect('payment_select', pk=order.pk)

    order.payment_method = 'card'
    order.payment_status = 'pending'
    order.save(update_fields=['payment_method', 'payment_status'])
    return redirect(session_url)


@login_required
def payment_start_mobile(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    if request.method != 'POST':
        return redirect('payment_select', pk=order.pk)

    phone = request.POST.get('phone', '').strip()
    if not phone:
        messages.error(request, 'Please enter a phone number for Mobile Money payment.')
        return redirect('payment_select', pk=order.pk)

    redirect_url = request.build_absolute_uri(reverse('payment_success', args=[order.pk]))
    link, error = payments.create_flutterwave_payment(order, redirect_url, customer_phone=phone)
    if error:
        messages.error(request, error)
        return redirect('payment_select', pk=order.pk)

    order.payment_method = 'mobile_money'
    order.payment_status = 'pending'
    order.save(update_fields=['payment_method', 'payment_status'])
    return redirect(link)


@login_required
def payment_success(request, pk):
    """Landing page after returning from Stripe or Flutterwave — verifies payment."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)

    if order.payment_method == 'card':
        session_id = request.GET.get('session_id', '')
        paid, ref = payments.verify_stripe_session(session_id) if session_id else (False, '')
    elif order.payment_method == 'mobile_money':
        tx_id = request.GET.get('transaction_id', '')
        paid, ref = payments.verify_flutterwave_transaction(tx_id) if tx_id else (False, '')
    else:
        paid, ref = False, ''

    if paid:
        order.payment_status = 'paid'
        order.payment_reference = ref
        order.paid_at = timezone.now()
        order.save(update_fields=['payment_status', 'payment_reference', 'paid_at'])
        send_order_confirmation_email(order)
        messages.success(request, f'Payment confirmed for Order #{order.pk}. Thank you!')
    else:
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        messages.warning(request, 'We could not confirm your payment yet. If you completed payment, it may take a few minutes to reflect — contact support if this persists.')

    return redirect('order_detail', pk=order.pk)
