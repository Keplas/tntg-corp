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
    """Redirects to cart — all orders now go through cart checkout."""
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    messages.success(request, 'Item added to your cart.')
    return redirect('cart')
    # Out of stock check
    if product.quantity_available is not None and product.quantity_available <= 0:
        messages.error(request, f'{product.name} is currently out of stock. Please check back soon.')
        return redirect('product_detail', pk=pk)
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

    # Detect market type from query param, session or user profile
    market = (request.GET.get('market')
              or request.session.get('market_type')
              or getattr(request.user, 'market_type', 'local'))
    if market not in ('local','international'):
        market = 'local'
    request.session['market_type'] = market  # remember for session

    return render(request, 'marketplace/place_order.html', {
        'product':          product,
        'settings':         settings,
        'session_referral': session_referral,
        'market':           market,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    
    STEPS = [
        ('pending',      'Order Placed',     'clock'),
        ('processing',   'Processing',       'cog'),
        ('accepted',     'Confirmed',        'check'),
        ('shipped',      'Shipped',          'truck'),
        ('delivered',    'Delivered',        'box-open'),
    ]
    step_keys = [s[0] for s in STEPS]
    current_step = step_keys.index(order.status) + 1 if order.status in step_keys else 1
    return render(request, 'marketplace/order_detail.html', {
        'order': order, 'steps': STEPS, 'current_step': current_step
    })


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


# ════════════════════════════════════════════════════════════════════════
# SHOPPING CART (session-based)
# ════════════════════════════════════════════════════════════════════════

def cart_view(request):
    cart  = request.session.get('cart', {})
    items = []
    total = decimal.Decimal('0')
    for pk_str, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pk_str), is_active=True)
            sub = p.price * qty
            total += sub
            items.append({'product': p, 'qty': qty, 'subtotal': sub})
        except Product.DoesNotExist:
            pass
    return render(request, 'marketplace/cart.html', {'items': items, 'total': total, 'count': len(items)})


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    qty  = max(1, int(request.POST.get('quantity', request.GET.get('quantity', 1))))
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + qty
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')


def cart_remove(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')


def cart_update(request, pk):
    qty  = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    if qty <= 0:
        cart.pop(str(pk), None)
    else:
        cart[str(pk)] = qty
    request.session['cart'] = cart
    return redirect('cart')


# ════════════════════════════════════════════════════════════════════════
# PRODUCT REVIEWS
# ════════════════════════════════════════════════════════════════════════

@login_required
def submit_review(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if request.method == 'POST':
        rating  = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment:
            exists = ProductReview.objects.filter(product=product, user=request.user).exists()
            if not exists:
                ProductReview.objects.create(
                    product=product, user=request.user,
                    rating=max(1, min(5, rating)), comment=comment
                )
                messages.success(request, 'Thank you for your review!')
            else:
                messages.warning(request, 'You have already reviewed this product.')
        else:
            messages.error(request, 'Please write a comment with your review.')
    return redirect('product_detail', pk=pk)


# ════════════════════════════════════════════════════════════════════════
# WISHLIST
# ════════════════════════════════════════════════════════════════════════

@login_required
def wishlist_toggle(request, pk):
    from .models import Wishlist
    product = get_object_or_404(Product, pk=pk, is_active=True)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        messages.info(request, f'Removed {product.name} from your wishlist.')
    else:
        messages.success(request, f'❤️ {product.name} saved to wishlist.')
    return redirect(request.META.get('HTTP_REFERER', reverse('product_detail', kwargs={'pk': pk})))


@login_required
def wishlist_view(request):
    from .models import Wishlist
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'marketplace/wishlist.html', {'items': items})


@login_required
def order_invoice(request, pk):
    from marketplace.models import Order
    order = get_object_or_404(Order, pk=pk)
    if not request.user.is_staff and order.buyer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('my_orders')
    return render(request, 'marketplace/order_invoice.html', {'order': order})


@login_required
def bulk_order_request(request):
    """Wholesale / bulk order enquiry form."""
    from .models import BulkOrder
    if request.method == 'POST':
        d = request.POST
        try:
            qty = float(d.get('quantity_kg', 0) or 0)
        except Exception:
            qty = 0
        BulkOrder.objects.create(
            buyer=request.user,
            company_name=d.get('company_name','').strip(),
            destination=d.get('destination','').strip(),
            product_type=d.get('product_type','').strip(),
            quantity_kg=qty,
            frequency=d.get('frequency','').strip(),
            notes=d.get('notes','').strip(),
        )
        # Notify admin
        try:
            from core.models import Notification
            Notification.notify('sell_order',
                f'Bulk Order Request — {request.user.username}',
                f'{qty}kg {d.get("product_type","")} to {d.get("destination","")}',
                '/admin/marketplace/bulkorder/')
        except Exception:
            pass
        # Email admin
        try:
            from django.core.mail import send_mail
            from django.conf import settings as djsettings
            send_mail(
                subject=f'New Bulk Order Request — {request.user.get_full_name() or request.user.username}',
                message=(f'Bulk order from {request.user.email}\n\n'
                         f'Company: {d.get("company_name","")}\n'
                         f'Product: {d.get("product_type","")}\n'
                         f'Quantity: {qty} kg\n'
                         f'Destination: {d.get("destination","")}\n'
                         f'Frequency: {d.get("frequency","")}\n'
                         f'Notes: {d.get("notes","")}'),
                from_email=getattr(djsettings,'DEFAULT_FROM_EMAIL',''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(request,
            'Bulk order request submitted! Our team will send you a custom quote within 2 business days.')
        return redirect('bulk_order_request')

    tiers = [
        {'range':'1 – 24 kg',    'discount':'Standard retail rate','note':'Available in online shop'},
        {'range':'25 – 99 kg',   'discount':'Negotiable rate',      'note':'Contact for quote'},
        {'range':'100 – 499 kg', 'discount':'5% bulk discount',     'note':'B2B pricing'},
        {'range':'500 – 999 kg', 'discount':'10% bulk discount',    'note':'Wholesale tier'},
        {'range':'1,000 kg+',    'discount':'Custom pricing',       'note':'Enterprise / export'},
    ]
    return render(request, 'marketplace/bulk_order.html', {'tiers': tiers})


@login_required
def manage_products(request):
    """Staff-only product image and detail management."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    products = Product.objects.all().order_by('name')
    return render(request, 'marketplace/manage_products.html', {'products': products})


@login_required
def update_product_image(request, pk):
    """Staff: update a product's Cloudinary image URL or upload new photo."""
    from django.shortcuts import get_object_or_404
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # Handle direct Cloudinary URL paste
        image_url = request.POST.get('image_url', '').strip()
        # Handle file upload (goes to Cloudinary via CloudinaryField)
        image_file = request.FILES.get('image')

        if image_file:
            product.image     = image_file
            product.image_url = ''   # clear URL when uploading a file
            product.save()
            messages.success(request, f'Photo uploaded to Cloudinary for {product.name}')
        elif image_url:
            product.image     = None   # clear CloudinaryField when using URL
            product.image_url = image_url
            product.save()
            messages.success(request, f'Image URL saved for {product.name}')
        else:
            messages.error(request, 'Please upload a photo or paste a Cloudinary URL.')

        return redirect('manage_products')

    return render(request, 'marketplace/update_product_image.html', {'product': product})


@login_required
def manage_product_prices(request, pk):
    from django.shortcuts import get_object_or_404
    from .models import ProductCountryPrice
    if not request.user.is_staff:
        return redirect('dashboard')

    product = get_object_or_404(Product, pk=pk)

    COUNTRY_CONFIG = [
        ('Canada',      'CAD', '🇨🇦'),
        ('USA',         'USD', '🇺🇸'),
        ('Uganda',      'UGX', '🇺🇬'),
        ('Kenya',       'KES', '🇰🇪'),
        ('Netherlands', 'EUR', '🇳🇱'),
        ('Japan',       'JPY', '🇯🇵'),
    ]

    if request.method == 'POST':
        for country, currency, flag in COUNTRY_CONFIG:
            price_val = request.POST.get(f'price_{country}','').strip()
            enabled   = request.POST.get(f'enabled_{country}')
            if price_val:
                try:
                    ProductCountryPrice.objects.update_or_create(
                        product=product, country=country,
                        defaults={
                            'price':     float(price_val),
                            'currency':  currency,
                            'is_active': bool(enabled),
                        }
                    )
                except Exception:
                    pass
            else:
                # If cleared — deactivate override (fall back to auto-rate)
                ProductCountryPrice.objects.filter(
                    product=product, country=country
                ).update(is_active=False)

        messages.success(request, f'Prices updated for {product.name}')
        return redirect('manage_products')

    # Get current overrides
    overrides = {op.country: op for op in product.country_prices.all()}
    auto_prices = product.get_country_prices()
    country_rows = []
    for cp in auto_prices:
        override = overrides.get(cp['country'])
        country_rows.append({
            'country':    cp['country'],
            'flag':       cp['flag'],
            'currency':   cp['currency'],
            'auto_price': cp['price'],
            'override':   override,
        })

    return render(request, 'marketplace/manage_product_prices.html', {
        'product': product,
        'country_rows': country_rows,
    })


@login_required
def cart_checkout(request):
    """Process all cart items — charge in buyer selected currency."""
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    display_currency = request.session.get('display_currency', 'CAD')
    STATIC_RATES = {'CAD':1.36,'USD':1.0,'UGX':3750.0,'KES':129.0,'EUR':0.92,'JPY':157.0}
    try:
        from core.exchange_rates import fetch_live_rates
        raw_rates = fetch_live_rates() or STATIC_RATES
    except Exception:
        raw_rates = STATIC_RATES

    def convert(amount, from_curr, to_curr):
        if from_curr == to_curr:
            return decimal.Decimal(str(amount))
        fr = decimal.Decimal(str(raw_rates.get(from_curr, 1) or 1))
        to = decimal.Decimal(str(raw_rates.get(to_curr, 1) or 1))
        return ((decimal.Decimal(str(amount)) / fr) * to).quantize(decimal.Decimal('0.01'))

    SYMBOLS = {'CAD':'CA$','USD':'US$','UGX':'UGX ','KES':'KES ','EUR':'€','JPY':'¥'}
    locked_rate = decimal.Decimal(str(raw_rates.get(display_currency, 1)))

    items = []
    total_display = decimal.Decimal('0')
    total_base    = decimal.Decimal('0')

    for pk_str, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pk_str), is_active=True)
            sub_base    = p.price * qty
            sub_display = convert(sub_base, p.currency, display_currency)
            total_base    += sub_base
            total_display += sub_display
            items.append({'product': p, 'qty': qty, 'subtotal': sub_display, 'base_subtotal': sub_base})
        except Product.DoesNotExist:
            pass

    if not items:
        messages.error(request, 'No valid items in cart.')
        return redirect('cart')

    if request.method == 'POST':
        try:
            destination   = request.POST.get('destination', '').strip()
            delivery_type = request.POST.get('delivery_type', 'ordinary')
            order_type    = request.POST.get('order_type', 'buy')
            referred_by   = request.POST.get('referral_code', '').strip()

            if delivery_type not in ('express', 'ordinary'):
                delivery_type = 'ordinary'
            if order_type not in ('buy', 'sell'):
                order_type = 'buy'

            settings    = LoyaltySettings.get_settings()
            reward_date = date.today() + timedelta(days=settings.payment_days)
            rate        = decimal.Decimal(str(settings.referral_rate if referred_by else settings.consumer_rate))
            tx_type     = 'earn_referral' if referred_by else 'earn_purchase'

            orders_created = []

            for item in items:
                product  = item['product']
                qty      = item['qty']
                base_sub = item['base_subtotal']
                disp_sub = item['subtotal']
                pts      = (base_sub * rate).quantize(decimal.Decimal('0.01'))

                if product.quantity_available is not None and product.quantity_available < qty:
                    messages.warning(request, f'Only {product.quantity_available} kg of {product.name} available.')
                    continue

                order = Order.objects.create(
                    buyer                = request.user,
                    product              = product,
                    order_type           = order_type,
                    quantity             = qty,
                    total_price          = base_sub,
                    delivery_type        = delivery_type,
                    destination_country  = destination,
                    destination_address  = destination_address,
                    desired_arrival_date = arrival_date,
                    desired_arrival_time = arrival_time,
                    referred_by          = referred_by,
                    referrer_unique_id   = referred_by,
                    avon_points_earned   = pts,
                    reward_payment_date  = reward_date,
                )

                # Save currency fields (safe if migration not yet run on Neon)
                try:
                    order.display_currency   = display_currency
                    order.display_total      = disp_sub
                    order.exchange_rate_used = locked_rate
                    order.save(update_fields=['display_currency', 'display_total', 'exchange_rate_used'])
                except Exception:
                    pass

                # Update stock
                try:
                    if product.quantity_available is not None:
                        product.quantity_available = max(0, product.quantity_available - qty)
                        product.save()
                except Exception:
                    pass

                # Credit loyalty points
                try:
                    request.user.avon_points = (request.user.avon_points or decimal.Decimal('0')) + pts
                    request.user.save(update_fields=['avon_points'])
                    AvonPointTransaction.objects.create(
                        user             = request.user,
                        transaction_type = tx_type,
                        points           = pts,
                        description      = f'Earned from Order #{order.pk}: {product.name}',
                        status           = 'completed',
                        min_execution_date = reward_date,
                    )
                except Exception:
                    pass

                # Notify admin
                try:
                    Notification.notify(
                        'order_placed',
                        f'New Order #{order.pk} — {product.name}',
                        f'Buyer: {request.user.get_full_name() or request.user.username} | {display_currency} {disp_sub}',
                        f'/admin/marketplace/order/{order.pk}/change/'
                    )
                except Exception:
                    pass

                # Send confirmation email
                try:
                    send_order_placed_email(order)
                except Exception:
                    pass

                orders_created.append(order)

            if orders_created:
                request.session['cart'] = {}
                messages.success(request,
                    f'{len(orders_created)} order(s) placed in {display_currency}!')
                return redirect('payment_select', pk=orders_created[0].pk)

            messages.error(request, 'No orders placed. Please check stock availability.')
            return redirect('cart')

        except Exception as e:
            messages.error(request, f'Something went wrong: {str(e)[:150]}. Please try again.')
            return redirect('cart')

    from datetime import datetime
    min_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    return render(request, 'marketplace/cart_checkout.html', {
        'items':            items,
        'min_date':         min_date,
        'total':            total_display,
        'display_currency': display_currency,
        'symbol':           SYMBOLS.get(display_currency, display_currency + ' '),
        'locked_rate':      locked_rate,
    })


def set_currency(request):
    """Save selected currency to session."""
    from django.http import JsonResponse
    VALID = ['CAD','USD','UGX','KES','EUR','JPY']
    if request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            currency = body.get('currency','CAD').upper()
        except Exception:
            currency = request.POST.get('currency','CAD').upper()
        if currency in VALID:
            request.session['display_currency'] = currency
        return JsonResponse({'currency': request.session.get('display_currency','CAD')})
    return JsonResponse({'currency': request.session.get('display_currency','CAD')})
