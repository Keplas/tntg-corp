from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date
from .models import Product, Order, ProductReview
from accounts.models import AvonPointTransaction
from core.models import Notification, LoyaltySettings
import decimal


def product_list(request):
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
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.all()[:10]
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    ctx = {'product': product, 'reviews': reviews, 'related': related}
    return render(request, 'marketplace/product_detail.html', ctx)


@login_required
def place_order(request, pk):
    product  = get_object_or_404(Product, pk=pk, is_active=True)
    settings = LoyaltySettings.get_settings()

    if request.method == 'POST':
        qty          = int(request.POST.get('quantity', 1))
        delivery     = request.POST.get('delivery_type', 'ordinary')
        dest_country = request.POST.get('destination_country', '')
        dest_address = request.POST.get('destination_address', '')
        arrival_date = request.POST.get('desired_arrival_date', '')
        arrival_time = request.POST.get('desired_arrival_time', '') or None
        referred_by  = request.POST.get('referred_by', '')
        referrer_id  = request.POST.get('referrer_unique_id', '')

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

        rate_pct = float(rate) * 100
        messages.success(
            request,
            f'Order placed! You earned {pts} T&TG Loyalty Points '
            f'({rate_pct:.1f}% of ${total}). '
            f'Reward payment scheduled for {reward_date.strftime("%d %b %Y")}.'
        )
        return redirect('order_detail', pk=order.pk)

    return render(request, 'marketplace/place_order.html', {
        'product':  product,
        'settings': settings,
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
