from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from marketplace.models import Product
from training.models import TrainingProgram, TVProgram
from services.models import ContactInquiry, ForexRate
from .models import Notification

def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]
    latest_products = Product.objects.filter(is_active=True)[:8]
    training_programs = TrainingProgram.objects.filter(is_active=True)[:3]
    tv_programs = TVProgram.objects.filter(is_active=True)[:3]
    forex_rates = ForexRate.objects.all()[:6]
    ctx = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'training_programs': training_programs,
        'tv_programs': tv_programs,
        'forex_rates': forex_rates,
        'countries': ['Canada', 'Uganda', 'Netherlands', 'USA', 'Kenya', 'Japan'],
        'stats': {
            'products': Product.objects.filter(is_active=True).count(),
            'countries': 6,
            'partners': 50,
            'transactions': 1200,
        }
    }
    return render(request, 'core/home.html', ctx)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        ContactInquiry.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            country=request.POST.get('country', ''),
            inquiry_type=request.POST.get('inquiry_type', 'general'),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        Notification.notify(
            'contact',
            f"New Contact Inquiry from {request.POST.get('name','')}",
            f"Subject: {request.POST.get('subject','')} | Email: {request.POST.get('email','')}",
            '/notifications/'
        )
        messages.success(request, 'Your message has been sent. We will get back to you shortly.')
        return redirect('contact')
    return render(request, 'core/contact.html')

def coffee(request):
    coffee_products = Product.objects.filter(category='coffee', is_active=True)
    ctx = {
        'coffee_products': coffee_products,
        'projections': [
            {'level': 1, 'kg_week': 25, 'monthly_low': 875, 'monthly_high': 1375, 'annual_low': 10500, 'annual_high': 16500},
            {'level': 2, 'kg_week': 50, 'monthly_low': 1750, 'monthly_high': 2750, 'annual_low': 21000, 'annual_high': 33000},
            {'level': 3, 'kg_week': 75, 'monthly_low': 2625, 'monthly_high': 4125, 'annual_low': 31500, 'annual_high': 49500},
            {'level': 4, 'kg_week': 100, 'monthly_low': 14000, 'monthly_high': 22000, 'annual_low': 168000, 'annual_high': 264000},
        ]
    }
    return render(request, 'core/coffee.html', ctx)

def avon_points_info(request):
    return render(request, 'core/avon_points.html')

@staff_member_required
def notifications(request):
    notifs = Notification.objects.all()[:100]
    unread_count = Notification.objects.filter(is_read=False).count()
    ctx = {'notifs': notifs, 'unread_count': unread_count}
    return render(request, 'core/notifications.html', ctx)

@staff_member_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.is_read = True
    notif.save()
    return redirect(notif.link or 'notifications')

@staff_member_required
def mark_all_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')

def notification_count(request):
    if request.user.is_staff:
        count = Notification.objects.filter(is_read=False).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})
