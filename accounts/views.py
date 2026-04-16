from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta, date
from .models import CustomUser, AvonPointTransaction
from marketplace.models import Order
from services.models import InsurancePolicy, BrokerageAccount
from core.models import Notification

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
        if request.FILES.get('national_id_front'):
            user.national_id_front = request.FILES['national_id_front']
        if request.FILES.get('national_id_back'):
            user.national_id_back = request.FILES['national_id_back']
        if request.FILES.get('selfie'):
            user.selfie = request.FILES['selfie']
        if request.FILES.get('declaration'):
            user.declaration = request.FILES['declaration']
        user.save()
        Notification.notify(
            'registration',
            f"New User Registered: {user.get_full_name() or user.username}",
            f"ID: {user.unique_id} | Country: {user.get_country_display()} | Market: {user.get_market_type_display()} | Role: {user.get_user_role_display()}",
            f'/admin/accounts/customuser/{user.pk}/change/'
        )
        if user.national_id_front or user.selfie:
            Notification.notify(
                'kyc',
                f"KYC Documents Submitted by {user.get_full_name() or user.username}",
                f"User {user.unique_id} has submitted identity documents for verification.",
                f'/admin/accounts/customuser/{user.pk}/change/'
            )
        login(request, user)
        messages.success(request, f'Welcome to T&TG Trade Corp! Your ID is {user.unique_id}.')
        return redirect('dashboard')
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
    recent_orders = Order.objects.filter(buyer=user).order_by('-created_at')[:5]
    recent_transactions = AvonPointTransaction.objects.filter(user=user).order_by('-created_at')[:5]
    insurance = InsurancePolicy.objects.filter(user=user, status='active')[:3]
    brokerage = BrokerageAccount.objects.filter(user=user)[:3]
    ctx = {
        'user': user,
        'recent_orders': recent_orders,
        'recent_transactions': recent_transactions,
        'insurance': insurance,
        'brokerage': brokerage,
        'total_orders': Order.objects.filter(buyer=user).count(),
        'pending_orders': Order.objects.filter(buyer=user, status='pending').count(),
    }
    return render(request, 'accounts/dashboard.html', ctx)

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.city = request.POST.get('city', user.city)
        user.address = request.POST.get('address', user.address)
        user.bio = request.POST.get('bio', user.bio)
        user.website = request.POST.get('website', user.website)
        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'accounts/profile.html')

@login_required
def avon_dashboard(request):
    user = request.user
    transactions = AvonPointTransaction.objects.filter(user=user).order_by('-created_at')
    if request.method == 'POST':
        action = request.POST.get('action')
        quarter = request.POST.get('quarter', 'Q1')
        if action == 'sell_order':
            pts = float(request.POST.get('points', 0))
            if pts > 0 and float(user.avon_points) >= pts:
                min_date = date.today() + timedelta(days=90)
                AvonPointTransaction.objects.create(
                    user=user, transaction_type='sell_order', points=pts,
                    quarter=quarter, status='pending', min_execution_date=min_date,
                    description=f"Sell order for {pts} points ({quarter})"
                )
                Notification.notify(
                    'sell_order',
                    f"Avon Points Sell Order — {user.get_full_name() or user.username}",
                    f"User {user.unique_id} placed a sell order for {pts} Avon Points ({quarter}). Min execution: {min_date}",
                    '/notifications/'
                )
                messages.success(request, f'Sell order for {pts} points placed. Min execution: {min_date}')
            else:
                messages.error(request, 'Insufficient points or invalid amount.')
        return redirect('avon_dashboard')
    ctx = {'transactions': transactions, 'quarters': ['Q1', 'Q2', 'Q3', 'Q4']}
    return render(request, 'accounts/avon_dashboard.html', ctx)

def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    products = profile_user.products.filter(is_active=True)[:6]
    return render(request, 'accounts/public_profile.html', {'profile_user': profile_user, 'products': products})
