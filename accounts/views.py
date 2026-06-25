from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date
from .models import CustomUser, AvonPointTransaction
from marketplace.models import Order
from core.models import Notification, LoyaltySettings


def register(request):
    if request.method == 'POST':
        d = request.POST
        if d.get('password') != d.get('confirm_password'):
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'post': d})
        if CustomUser.objects.filter(username=d.get('username')).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html', {'post': d})
        user = CustomUser.objects.create_user(
            username=d.get('username'),
            email=d.get('email'),
            password=d.get('password'),
            first_name=d.get('first_name', ''),
            last_name=d.get('last_name', ''),
            phone=d.get('phone', ''),
            country=d.get('country', ''),
            city=d.get('city', ''),
            address=d.get('address', ''),
            market_type=d.get('market_type', 'local'),
            user_role=d.get('user_role', 'buyer'),
            term_preference=d.get('term_preference', 'short'),
            business_description=d.get('business_description', ''),
            is_partner=d.get('is_partner', '') == 'on',
            partner_company=d.get('partner_company', ''),
        )
        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']
            user.save(update_fields=['profile_photo'])

        Notification.notify(
            'registration',
            f"New User Registered: {user.get_full_name() or user.username}",
            (
                f"ID: {user.unique_id} | Country: {user.get_country_display()} | "
                f"Market: {user.get_market_type_display()} | Role: {user.get_user_role_display()}"
            ),
            f'/admin/accounts/customuser/{user.pk}/change/'
        )

        login(request, user, backend="accounts.backends.FlexAuthBackend")
        messages.success(request, f'Welcome to T&TG Trade Corp! Your ID is {user.unique_id}.')
        return redirect('dashboard')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password   = request.POST.get('password', '')
        user = authenticate(request, username=identifier, password=password)
        if user:
            login(request, user, backend="accounts.backends.FlexAuthBackend")
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username, email or password.')
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
@login_required
def dashboard(request):
    """Unified admin dashboard — Dashboard + Profile + Loyalty + Analytics + Notifications."""
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncDate
    from datetime import timedelta, date
    from marketplace.models import Order, Product
    from core.models import Notification, LoyaltySettings, BlogPost

    user     = request.user
    settings = LoyaltySettings.get_settings()

    # ── Profile form POST ─────────────────────────────────────────────────────
    if request.method == 'POST' and request.POST.get('action') == 'profile':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name',  user.last_name)
        user.phone      = request.POST.get('phone',      user.phone)
        user.city       = request.POST.get('city',       user.city)
        user.address    = request.POST.get('address',    user.address)
        user.bio        = request.POST.get('bio',        user.bio)
        user.website    = request.POST.get('website',    user.website)
        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']
        user.save(update_fields=[
            'first_name','last_name','phone','city',
            'address','bio','website','profile_photo',
        ])
        messages.success(request, 'Profile updated successfully.')
        return redirect(reverse('dashboard') + '#profile')

    # ── Loyalty withdrawal POST ───────────────────────────────────────────────
    if request.method == 'POST' and request.POST.get('action') == 'withdrawal':
        quarter = request.POST.get('quarter', 'Q1')
        pts = float(request.POST.get('points', 0))
        if pts > 0 and float(user.avon_points) >= pts:
            pay_date = date.today() + timedelta(days=settings.payment_days)
            AvonPointTransaction.objects.create(
                user=user, transaction_type='withdrawal',
                points=pts, quarter=quarter, status='pending',
                min_execution_date=pay_date,
                description=f"Withdrawal of {pts} T&TG Loyalty Points ({quarter})"
            )
            Notification.notify(
                'sell_order',
                f"Loyalty Points Withdrawal — {user.get_full_name() or user.username}",
                f"User {user.unique_id} requested withdrawal of {pts} points ({quarter}). Payment due: {pay_date}",
                '/analytics/'
            )
            messages.success(request, f'Withdrawal of {pts} points submitted. Payment by {pay_date.strftime("%d %b %Y")}.')
        else:
            messages.error(request, 'Insufficient points or invalid amount.')
        return redirect(reverse('dashboard') + '#loyalty')

    # ── User Dashboard data ───────────────────────────────────────────────────
    recent_orders       = Order.objects.filter(buyer=user).order_by('-created_at')[:5]
    recent_transactions = AvonPointTransaction.objects.filter(user=user).order_by('-created_at')[:5]
    total_orders        = Order.objects.filter(buyer=user).count()
    pending_orders      = Order.objects.filter(buyer=user, status='pending').count()

    # ── Loyalty data ──────────────────────────────────────────────────────────
    transactions  = AvonPointTransaction.objects.filter(user=user).order_by('-created_at')
    earned_txns   = transactions.filter(transaction_type__startswith='earn_')
    referral_txns = transactions.filter(transaction_type='earn_referral')
    withdraw_txns = transactions.filter(transaction_type='withdrawal')
    quarters      = ['Q1','Q2','Q3','Q4']

    ctx = {
        'user': user, 'settings': settings,
        # dashboard
        'recent_orders': recent_orders, 'recent_transactions': recent_transactions,
        'total_orders': total_orders, 'pending_orders': pending_orders,
        'loyalty_settings': settings,
        # loyalty
        'transactions': transactions, 'earned_txns': earned_txns,
        'referral_txns': referral_txns, 'withdraw_txns': withdraw_txns,
        'quarters': quarters,
    }

    # ── Analytics (staff only) ────────────────────────────────────────────────
    if user.is_staff:
        today           = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        orders_30d      = Order.objects.filter(created_at__date__gte=thirty_days_ago)

        daily_sales = (
            orders_30d.annotate(day=TruncDate('created_at'))
            .values('day').annotate(total=Sum('total_price'), count=Count('id'))
            .order_by('day')
        )

        notifs       = Notification.objects.all()[:100]
        unread_count = Notification.objects.filter(is_read=False).count()

        ctx.update({
            'is_staff_view': True,
            'total_revenue':        Order.objects.aggregate(s=Sum('total_price'))['s'] or 0,
            'total_orders_all':     Order.objects.count(),
            'avg_order_value':      Order.objects.aggregate(a=Avg('total_price'))['a'] or 0,
            'total_customers':      CustomUser.objects.filter(orders__isnull=False).distinct().count(),
            'total_points_issued':  AvonPointTransaction.objects.filter(
                                        transaction_type__in=['earn_purchase','earn_referral']
                                    ).aggregate(s=Sum('points'))['s'] or 0,
            'pending_payouts':      AvonPointTransaction.objects.filter(status='pending').aggregate(s=Sum('points'))['s'] or 0,
            'total_products_active': Product.objects.filter(is_active=True).count(),
            'sales_labels':  [d['day'].strftime('%b %d') for d in daily_sales],
            'sales_values':  [float(d['total'] or 0) for d in daily_sales],
            'top_products':  Order.objects.values('product__name').annotate(revenue=Sum('total_price'), units=Sum('quantity')).order_by('-revenue')[:8],
            'status_breakdown': Order.objects.values('status').annotate(count=Count('id')).order_by('-count'),
            'payment_breakdown': Order.objects.values('payment_status').annotate(count=Count('id')).order_by('-count'),
            'category_sales': Order.objects.values('product__category').annotate(revenue=Sum('total_price'), units=Sum('quantity')).order_by('-revenue'),
            'country_breakdown': Order.objects.values('destination_country').annotate(count=Count('id'), revenue=Sum('total_price')).order_by('-revenue')[:6],
            'notifs': notifs, 'unread_count': unread_count,
        })

    return render(request, 'accounts/dashboard.html', ctx)


@login_required
def profile(request):
    """Redirect to unified dashboard #profile section."""
    return redirect(reverse('dashboard') + '#profile')


@login_required
def loyalty_dashboard(request):
    """T&TG Trade Loyalty Platform — Points, Promotions, Referral, Reward."""
    user     = request.user
    settings = LoyaltySettings.get_settings()
    transactions = AvonPointTransaction.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        action  = request.POST.get('action')
        quarter = request.POST.get('quarter', 'Q1')

        if action == 'withdrawal':
            pts = float(request.POST.get('points', 0))
            if pts > 0 and float(user.avon_points) >= pts:
                pay_date = date.today() + timedelta(days=settings.payment_days)
                AvonPointTransaction.objects.create(
                    user             = user,
                    transaction_type = 'withdrawal',
                    points           = pts,
                    quarter          = quarter,
                    status           = 'pending',
                    min_execution_date = pay_date,
                    description      = f"Withdrawal of {pts} T&TG Loyalty Points ({quarter})"
                )
                Notification.notify(
                    'sell_order',
                    f"Loyalty Points Withdrawal — {user.get_full_name() or user.username}",
                    (
                        f"User {user.unique_id} requested withdrawal of {pts} T&TG Loyalty Points "
                        f"({quarter}). Payment due: {pay_date}"
                    ),
                    '/notifications/'
                )
                messages.success(
                    request,
                    f'Withdrawal of {pts} T&TG Loyalty Points submitted. '
                    f'Payment will be processed by {pay_date.strftime("%d %b %Y")}.'
                )
            else:
                messages.error(request, 'Insufficient points or invalid amount.')
        return redirect('loyalty_dashboard')

    # Split transactions by type for the four tabs
    earned_txns   = transactions.filter(transaction_type__startswith='earn_')
    referral_txns = transactions.filter(transaction_type='earn_referral')
    withdraw_txns = transactions.filter(transaction_type='withdrawal')

    ctx = {
        'transactions':   transactions,
        'earned_txns':    earned_txns,
        'referral_txns':  referral_txns,
        'withdraw_txns':  withdraw_txns,
        'quarters':       ['Q1', 'Q2', 'Q3', 'Q4'],
        'settings':       settings,
    }
    return render(request, 'accounts/loyalty_dashboard.html', ctx)


# Keep the old URL name working as a redirect
@login_required
def avon_dashboard(request):
    return redirect('loyalty_dashboard')


def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    products     = profile_user.products.filter(is_active=True)[:6]
    return render(request, 'accounts/public_profile.html', {
        'profile_user': profile_user,
        'products':     products,
    })
