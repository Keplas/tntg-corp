from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
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

        # Send email verification
        import secrets, hashlib
        from django.core.mail import send_mail
        from django.conf import settings as djsettings
        token = secrets.token_urlsafe(32)
        user.email_verify_token = hashlib.sha256(token.encode()).hexdigest()
        user.save(update_fields=['email_verify_token'])
        verify_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )
        try:
            send_mail(
                subject='Verify your T&TG Trade Corp email',
                message=(
                    f'Hi {user.first_name or user.username},\n\n'
                    f'Welcome to T&TG Trade Corp! Please verify your email:\n\n'
                    f'{verify_url}\n\n'
                    f'Your unique ID is: {user.unique_id}\n\n'
                    f'If you did not create this account, ignore this email.\n\nT&TG Trade Corp'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        try:
            Notification.notify(
                'registration',
                f"New User Registered: {user.get_full_name() or user.username}",
                (
                    f"ID: {user.unique_id} | Country: {user.get_country_display()} | "
                    f"Market: {user.get_market_type_display()} | Role: {user.get_user_role_display()}"
                ),
                f'/admin/accounts/customuser/{user.pk}/change/'
            )
        except Exception:
            pass

        login(request, user, backend="accounts.backends.FlexAuthBackend")
        messages.success(request, f'Welcome to T&TG Trade Corp! Your ID is {user.unique_id}. Check your email to verify your account.')
        return redirect('dashboard')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        from django.conf import settings as djsettings
        identifier = request.POST.get('username', '').strip()
        password   = request.POST.get('password', '')

        # Find user object for lockout tracking
        user_obj = None
        for lookup in ['username__iexact', 'email__iexact', 'phone']:
            try:
                user_obj = CustomUser.objects.get(**{lookup: identifier})
                break
            except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                pass

        # Check lockout
        if user_obj and user_obj.locked_until:
            if timezone.now() < user_obj.locked_until:
                remaining = int((user_obj.locked_until - timezone.now()).total_seconds() // 60) + 1
                messages.error(request, f'Account locked. Try again in {remaining} minute(s).')
                return render(request, 'accounts/login.html')
            else:
                user_obj.login_attempts = 0
                user_obj.locked_until   = None
                user_obj.save(update_fields=['login_attempts', 'locked_until'])

        user = authenticate(request, username=identifier, password=password)

        if user:
            user.login_attempts = 0
            user.locked_until   = None
            user.save(update_fields=['login_attempts', 'locked_until'])
            login(request, user, backend='accounts.backends.FlexAuthBackend')
            return redirect(request.GET.get('next', 'dashboard'))

        # Failed attempt
        if user_obj:
            user_obj.login_attempts += 1
            max_att     = getattr(djsettings, 'MAX_LOGIN_ATTEMPTS', 5)
            lockout_min = getattr(djsettings, 'LOCKOUT_MINUTES', 30)
            if user_obj.login_attempts >= max_att:
                from datetime import timedelta as td
                user_obj.locked_until = timezone.now() + td(minutes=lockout_min)
                user_obj.save(update_fields=['login_attempts', 'locked_until'])
                messages.error(request, f'Too many failed attempts. Account locked for {lockout_min} minutes.')
            else:
                left = max_att - user_obj.login_attempts
                user_obj.save(update_fields=['login_attempts'])
                messages.error(request, f'Invalid credentials. {left} attempt(s) left before lockout.')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'accounts/login.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


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
        from django.contrib.auth.hashers import check_password as chk_pw
        from django.core.mail import send_mail
        from django.conf import settings as djsettings

        quarter = request.POST.get('quarter', 'Q1')
        pts     = float(request.POST.get('points', 0))
        pin     = request.POST.get('withdrawal_pin', '').strip()

        # Require PIN to be set
        if not user.withdrawal_pin_set:
            messages.error(request, 'Please set a withdrawal PIN before making withdrawals.')
            return redirect(reverse('set_withdrawal_pin'))

        # Verify PIN
        if not chk_pw(pin, user.withdrawal_pin):
            messages.error(request, 'Incorrect withdrawal PIN. Please try again.')
            return redirect(reverse('dashboard') + '#loyalty')

        # Check sufficient balance
        if pts <= 0 or float(user.avon_points) < pts:
            messages.error(request, 'Insufficient points or invalid amount.')
            return redirect(reverse('dashboard') + '#loyalty')

        # Check daily withdrawal limit
        from datetime import datetime
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_total = AvonPointTransaction.objects.filter(
            user=user, transaction_type='withdrawal',
            created_at__gte=today_start
        ).aggregate(s=Sum('points'))['s'] or 0
        daily_limit = float(user.daily_withdrawal_limit)
        if float(today_total) + pts > daily_limit:
            remaining_today = max(0, daily_limit - float(today_total))
            messages.error(request,
                f'Daily withdrawal limit is ${daily_limit:.0f}. '
                f'You have ${remaining_today:.2f} remaining today.')
            return redirect(reverse('dashboard') + '#loyalty')

        # All checks passed — create withdrawal
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

        # Email confirmation to user
        try:
            send_mail(
                subject='Withdrawal Request Confirmed — T&TG Trade Corp',
                message=(
                    f'Hi {user.first_name or user.username},\n\n'
                    f'Your withdrawal request has been received:\n\n'
                    f'  Amount: {pts} T&TG Loyalty Points (≈ ${pts:.2f} USD)\n'
                    f'  Quarter: {quarter}\n'
                    f'  Payment due: {pay_date.strftime("%d %B %Y")}\n\n'
                    f'If you did not request this withdrawal, contact us immediately.\n\n'
                    f'T&TG Trade Corp | {user.unique_id}'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request,
            f'Withdrawal of {pts} points submitted. Payment by {pay_date.strftime("%d %b %Y")}. '
            f'Confirmation sent to {user.email}.')
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


# ── Forgot / Reset password ────────────────────────────────────────────────────

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email__iexact=email)
            import secrets, hashlib
            from datetime import timedelta
            from django.core.mail import send_mail
            from django.conf import settings as djsettings

            token = secrets.token_urlsafe(32)
            user.password_reset_token   = hashlib.sha256(token.encode()).hexdigest()
            user.password_reset_expires = timezone.now() + timedelta(
                hours=getattr(djsettings, 'RESET_TOKEN_HOURS', 24)
            )
            user.save(update_fields=['password_reset_token', 'password_reset_expires'])

            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': token})
            )
            try:
                send_mail(
                    subject='Reset your T&TG password',
                    message=(
                        f'Hi {user.first_name or user.username},\n\n'
                        f'Click the link below to reset your password.\n'
                        f'This link expires in 24 hours.\n\n{reset_url}\n\n'
                        f'If you did not request this, ignore this email.\n\nT&TG Trade Corp'
                    ),
                    from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        except CustomUser.DoesNotExist:
            pass  # Don't reveal if email exists

        messages.success(request, 'If that email exists we\'ve sent a reset link. Check your inbox.')
        return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, token):
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        user = CustomUser.objects.get(
            password_reset_token=token_hash,
            password_reset_expires__gt=timezone.now()
        )
    except CustomUser.DoesNotExist:
        messages.error(request, 'This reset link is invalid or has expired.')
        return redirect('forgot_password')

    if request.method == 'POST':
        pw1 = request.POST.get('password', '')
        pw2 = request.POST.get('confirm_password', '')
        if pw1 != pw2:
            messages.error(request, 'Passwords do not match.')
        elif len(pw1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user.set_password(pw1)
            user.password_reset_token   = ''
            user.password_reset_expires = None
            user.login_attempts         = 0
            user.locked_until           = None
            user.save(update_fields=[
                'password', 'password_reset_token', 'password_reset_expires',
                'login_attempts', 'locked_until'
            ])
            messages.success(request, 'Password reset successfully. You can now sign in.')
            return redirect('login')

    return render(request, 'accounts/reset_password.html', {'token': token})


# ── Email verification ──────────────────────────────────────────────────────────

def verify_email(request, token):
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        user = CustomUser.objects.get(email_verify_token=token_hash)
        user.email_verified      = True
        user.email_verify_token  = ''
        user.save(update_fields=['email_verified', 'email_verify_token'])
        messages.success(request, 'Email verified! Your account is now fully active.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'This verification link is invalid or already used.')
    return redirect('dashboard')


# ── Withdrawal PIN ──────────────────────────────────────────────────────────────

@login_required
def set_withdrawal_pin(request):
    user = request.user
    if request.method == 'POST':
        from django.contrib.auth.hashers import make_password, check_password as chk_pw
        action = request.POST.get('action')

        if action == 'set_pin':
            pin     = request.POST.get('pin', '').strip()
            pin2    = request.POST.get('pin2', '').strip()
            current = request.POST.get('current_pin', '').strip()

            if not pin.isdigit() or len(pin) != 4:
                messages.error(request, 'PIN must be exactly 4 digits.')
            elif pin != pin2:
                messages.error(request, 'PINs do not match.')
            elif user.withdrawal_pin_set and not chk_pw(current, user.withdrawal_pin):
                messages.error(request, 'Current PIN is incorrect.')
            else:
                user.withdrawal_pin     = make_password(pin)
                user.withdrawal_pin_set = True
                user.save(update_fields=['withdrawal_pin', 'withdrawal_pin_set'])
                messages.success(request, 'Withdrawal PIN set successfully.')
                return redirect(reverse('dashboard') + '#loyalty')

    return render(request, 'accounts/set_pin.html')


# ════════════════════════════════════════════════════════════════════════
# MULTI-CURRENCY WALLET
# ════════════════════════════════════════════════════════════════════════

@login_required
def wallet_view(request):
    """User wallet — balances, transactions, convert, withdraw."""
    from .models import Wallet, WalletTransaction
    from decimal import Decimal

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet)[:30]

    # Get live forex rates for balance conversion display
    try:
        from core.exchange_rates import fetch_live_rates, build_pairs
        raw_rates = fetch_live_rates()
    except Exception:
        raw_rates = None

    # Build balance cards
    balances = []
    total_in_cad = Decimal('0')
    for code, label, symbol in Wallet.SUPPORTED:
        bal = wallet.get_balance(code)
        # Convert to CAD equivalent for total
        if raw_rates and bal > 0:
            try:
                if code == 'CAD':
                    cad_eq = bal
                elif code == 'USD':
                    cad_eq = bal * Decimal(str(raw_rates.get('CAD',1)))
                else:
                    usd_rate  = Decimal(str(raw_rates.get(code, 1)))
                    cad_rate  = Decimal(str(raw_rates.get('CAD', 1)))
                    cad_eq = (bal / usd_rate) * cad_rate if usd_rate else Decimal('0')
                total_in_cad += cad_eq
            except Exception:
                cad_eq = Decimal('0')
        else:
            cad_eq = Decimal('0')
        balances.append({'code': code, 'label': label, 'symbol': symbol,
                         'balance': bal, 'cad_eq': cad_eq})

    ctx = {
        'wallet':       wallet,
        'balances':     balances,
        'transactions': transactions,
        'total_cad':    total_in_cad,
        'has_balance':  any(b['balance'] > 0 for b in balances),
    }
    return render(request, 'accounts/wallet.html', ctx)


@login_required
def wallet_convert(request):
    """Convert between currencies using live rates."""
    from .models import Wallet, WalletTransaction
    from decimal import Decimal

    if request.method == 'POST':
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        from_c  = request.POST.get('from_currency','').upper()
        to_c    = request.POST.get('to_currency','').upper()
        try:
            amount = Decimal(request.POST.get('amount','0') or '0')
        except Exception:
            amount = Decimal('0')

        if from_c == to_c:
            messages.error(request, 'Please select two different currencies.')
        elif amount <= 0:
            messages.error(request, 'Please enter a valid amount.')
        elif wallet.get_balance(from_c) < amount:
            messages.error(request, f'Insufficient {from_c} balance.')
        else:
            try:
                from core.exchange_rates import fetch_live_rates
                raw = fetch_live_rates()
                if raw:
                    # Calculate cross rate via USD
                    if from_c == 'USD':
                        rate = Decimal(str(raw.get(to_c, 1)))
                    elif to_c == 'USD':
                        rate = Decimal('1') / Decimal(str(raw.get(from_c, 1)))
                    else:
                        rate = Decimal(str(raw.get(to_c, 1))) / Decimal(str(raw.get(from_c, 1)))

                    converted = (amount * rate).quantize(Decimal('0.0001'))
                    ref = f'CONV-{from_c}-{to_c}'
                    wallet.debit(from_c,  amount,    ref=ref, note=f'Converted {amount} {from_c} to {to_c}', created_by=request.user)
                    wallet.credit(to_c, converted, ref=ref, note=f'Received {converted} {to_c} from {from_c}', created_by=request.user)
                    # Save conversion transaction
                    WalletTransaction.objects.create(
                        wallet=wallet, currency=f'{from_c}>{to_c}',
                        amount=amount, transaction_type='conversion',
                        reference=ref,
                        note=f'{amount} {from_c} → {converted} {to_c} @ rate {rate:.6f}',
                        created_by=request.user
                    )
                    messages.success(request, f'Converted {amount} {from_c} → {converted} {to_c} successfully.')
                else:
                    messages.error(request, 'Live rates unavailable. Please try again later.')
            except Exception as e:
                messages.error(request, f'Conversion failed: {e}')

    return redirect('wallet')


@login_required
def wallet_withdraw(request):
    """Request a withdrawal from wallet."""
    from .models import Wallet
    from decimal import Decimal

    if request.method == 'POST':
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        currency = request.POST.get('currency','CAD').upper()
        try:
            amount = Decimal(request.POST.get('amount','0') or '0')
        except Exception:
            amount = Decimal('0')
        method  = request.POST.get('method','Bank Transfer')
        details = request.POST.get('details','').strip()

        if amount <= 0:
            messages.error(request, 'Please enter a valid amount.')
        elif wallet.get_balance(currency) < amount:
            messages.error(request, f'Insufficient {currency} balance. Available: {wallet.get_balance(currency)}')
        elif not details:
            messages.error(request, 'Please provide your payment details.')
        else:
            # Hold the amount (debit from wallet, mark as withdrawal pending)
            wallet.debit(currency, amount,
                ref=f'WD-{currency}',
                note=f'Withdrawal request via {method}. Details: {details}',
                created_by=request.user
            )
            # Notify admin
            try:
                from core.models import Notification
                Notification.notify(
                    'sell_order',
                    f'Withdrawal Request — {request.user.username}',
                    f'{amount} {currency} withdrawal via {method}. Details: {details}',
                    '/admin/accounts/wallettransaction/'
                )
            except Exception:
                pass
            messages.success(request, f'Withdrawal request of {amount} {currency} submitted. Processing on Day 45 cycle.')

    return redirect('wallet')


@login_required
def analytics_dashboard(request):
    """Admin-only analytics dashboard."""
    from marketplace.models import Order, Product, BulkOrder
    from services.models import TradeInquiry
    from core.models import Notification, NewsletterSubscriber
    from accounts.models import CustomUser
    from django.db.models import Sum, Avg, Count
    from django.utils import timezone
    from datetime import timedelta
    import decimal

    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    now   = timezone.now()
    month = now - timedelta(days=30)

    # Core stats
    try: total_revenue    = Order.objects.aggregate(s=Sum('total_price'))['s'] or decimal.Decimal('0')
    except: total_revenue = decimal.Decimal('0')
    try: monthly_revenue  = Order.objects.filter(created_at__gte=month).aggregate(s=Sum('total_price'))['s'] or decimal.Decimal('0')
    except: monthly_revenue = decimal.Decimal('0')
    try: avg_order        = Order.objects.aggregate(a=Avg('total_price'))['a'] or decimal.Decimal('0')
    except: avg_order     = decimal.Decimal('0')

    stats = {
        'total_users':      CustomUser.objects.count(),
        'total_orders':     Order.objects.count(),
        'pending_orders':   Order.objects.filter(status='pending').count(),
        'trade_inquiries':  TradeInquiry.objects.count(),
        'bulk_orders':      BulkOrder.objects.count(),
        'newsletter_subs':  NewsletterSubscriber.objects.filter(active=True).count(),
        'total_revenue':    total_revenue,
        'monthly_revenue':  monthly_revenue,
        'avg_order':        avg_order,
    }

    top_products = Product.objects.filter(is_active=True).annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:5]

    users_by_country = CustomUser.objects.values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:6]

    ctx = {
        'stats':          stats,
        'top_products':   top_products,
        'users_by_country': users_by_country,
        'recent_orders':  Order.objects.select_related('buyer','product').order_by('-created_at')[:8],
        'recent_trade':   TradeInquiry.objects.order_by('-created_at')[:6],
        'recent_notifs':  Notification.objects.order_by('-created_at')[:6],
    }
    return render(request, 'accounts/analytics_dashboard.html', ctx)
