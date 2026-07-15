from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from marketplace.models import Product
from training.models import TrainingProgram, TVProgram
from services.models import ContactInquiry, ForexRate
from .models import Notification, LoyaltySettings

OPERATION_COUNTRIES = [
    {'code': 'CA', 'name': 'Canada', 'flag': '🇨🇦'},
    {'code': 'UG', 'name': 'Uganda', 'flag': '🇺🇬'},
    {'code': 'KE', 'name': 'Kenya',  'flag': '🇰🇪'},
    {'code': 'US', 'name': 'USA',    'flag': '🇺🇸'},
]


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]
    latest_products   = Product.objects.filter(is_active=True)[:8]
    training_programs = TrainingProgram.objects.filter(is_active=True)[:3]
    tv_programs       = TVProgram.objects.filter(is_active=True)[:3]
    forex_rates       = ForexRate.objects.all()[:3]
    ctx = {
        'featured_products': featured_products,
        'latest_products':   latest_products,
        'training_programs': training_programs,
        'tv_programs':       tv_programs,
        'forex_rates':       forex_rates,
        'countries':         OPERATION_COUNTRIES,
        'stats': {
            'products':     Product.objects.filter(is_active=True).count(),
            'countries':    3,
            'partners':     50,
            'transactions': 1200,
        }
    }
    return render(request, 'core/home.html', ctx)


def about(request):
    return render(request, 'core/about.html', {'countries': OPERATION_COUNTRIES})


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


def loyalty_info(request):
    settings = LoyaltySettings.get_settings()
    return render(request, 'core/loyalty_info.html', {'settings': settings})


def coffee(request):
    """Coffee is now on the shopping platform — redirect to coffee products."""
    return redirect('/marketplace/products/?category=coffee')


@staff_member_required
def notifications(request):
    notifs       = Notification.objects.all()[:100]
    unread_count = Notification.objects.filter(is_read=False).count()
    return render(request, 'core/notifications.html', {'notifs': notifs, 'unread_count': unread_count})


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


# ═══════════════════════════════════════════════════════════════
# SEO — sitemap.xml and robots.txt as plain views (no extra apps
# or settings.py changes required — self-contained and safe to
# drop in regardless of other local project customisations).
# ═══════════════════════════════════════════════════════════════

def sitemap_xml(request):
    """Dynamic XML sitemap — static pages + all active products."""
    domain = request.build_absolute_uri('/')[:-1]  # e.g. https://tntgcorp.com

    static_pages = [
        {'loc': '/',                       'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/about/',                 'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': '/contact/',               'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': '/loyalty/',               'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': '/marketplace/products/',  'priority': '0.9', 'changefreq': 'daily'},
        {'loc': '/services/forex/',        'priority': '0.6', 'changefreq': 'daily'},
        {'loc': '/services/trade-ecommerce/', 'priority': '0.6', 'changefreq': 'weekly'},
        {'loc': '/training/',              'priority': '0.6', 'changefreq': 'weekly'},
    ]

    urls = []
    for page in static_pages:
        urls.append(f"  <url><loc>{domain}{page['loc']}</loc>"
                     f"<changefreq>{page['changefreq']}</changefreq>"
                     f"<priority>{page['priority']}</priority></url>")

    for product in Product.objects.filter(is_active=True):
        urls.append(f"  <url><loc>{domain}/marketplace/products/{product.pk}/</loc>"
                     f"<changefreq>weekly</changefreq><priority>0.7</priority></url>")

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(urls) +
           '\n</urlset>')

    return HttpResponse(xml, content_type='application/xml')


def robots_txt(request):
    """robots.txt — points crawlers to the sitemap, blocks admin/account areas."""
    domain = request.build_absolute_uri('/')[:-1]
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/dashboard/",
        "Disallow: /accounts/profile/",
        "Disallow: /marketplace/orders/",
        f"Sitemap: {domain}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type='text/plain')


@staff_member_required
def analytics_dashboard(request):
    """
    Admin analytics dashboard — sales trends, top products, order status
    breakdown, and loyalty points overview. Built entirely from existing
    Order/Product/AvonPointTransaction data — no new tracking required.
    """
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    from marketplace.models import Order, Product
    from accounts.models import AvonPointTransaction, CustomUser

    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    orders_30d = Order.objects.filter(created_at__date__gte=thirty_days_ago)

    # Revenue trend — daily totals for the last 30 days
    daily_sales = (
        orders_30d
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum('total_price'), count=Count('id'))
        .order_by('day')
    )
    sales_labels = [d['day'].strftime('%b %d') for d in daily_sales]
    sales_values = [float(d['total'] or 0) for d in daily_sales]

    # Top products by revenue (all-time)
    top_products = (
        Order.objects
        .values('product__name')
        .annotate(revenue=Sum('total_price'), units=Sum('quantity'))
        .order_by('-revenue')[:8]
    )

    # Order status breakdown
    status_breakdown = (
        Order.objects.values('status').annotate(count=Count('id')).order_by('-count')
    )

    # Payment status breakdown
    payment_breakdown = (
        Order.objects.values('payment_status').annotate(count=Count('id')).order_by('-count')
    )

    # Category performance
    category_sales = (
        Order.objects
        .values('product__category')
        .annotate(revenue=Sum('total_price'), units=Sum('quantity'))
        .order_by('-revenue')
    )

    # Headline stats
    total_revenue   = Order.objects.aggregate(s=Sum('total_price'))['s'] or 0
    total_orders    = Order.objects.count()
    avg_order_value = Order.objects.aggregate(a=Avg('total_price'))['a'] or 0
    total_customers = CustomUser.objects.filter(orders__isnull=False).distinct().count()
    total_points_issued = AvonPointTransaction.objects.filter(
        transaction_type__in=['earn_purchase', 'earn_referral']
    ).aggregate(s=Sum('points'))['s'] or 0
    pending_payouts = AvonPointTransaction.objects.filter(status='pending').aggregate(s=Sum('points'))['s'] or 0

    # Country breakdown (where orders are shipping to)
    country_breakdown = (
        Order.objects.values('destination_country')
        .annotate(count=Count('id'), revenue=Sum('total_price'))
        .order_by('-revenue')[:6]
    )

    ctx = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_customers': total_customers,
        'total_points_issued': total_points_issued,
        'pending_payouts': pending_payouts,
        'sales_labels': sales_labels,
        'sales_values': sales_values,
        'top_products': top_products,
        'status_breakdown': status_breakdown,
        'payment_breakdown': payment_breakdown,
        'category_sales': category_sales,
        'country_breakdown': country_breakdown,
        'total_products_active': Product.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/analytics_dashboard.html', ctx)


def set_language(request):
    """Toggle site language between English and Swahili — stored in session."""
    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'sw'):
        lang = 'en'
    request.session['lang'] = lang
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


# ── Withdrawal approval (staff only) ──────────────────────────────────────────
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_withdrawal(request, pk):
    from accounts.models import AvonPointTransaction
    from django.shortcuts import get_object_or_404
    from django.core.mail import send_mail
    from django.conf import settings as djsettings
    txn  = get_object_or_404(AvonPointTransaction, pk=pk, status='pending_approval')
    user = txn.user
    if float(user.avon_points) < float(txn.points):
        messages.error(request, f'Cannot approve: insufficient balance for {user.username}.')
        return redirect(request.META.get('HTTP_REFERER', '/accounts/dashboard/#notifications'))
    user.avon_points = float(user.avon_points) - float(txn.points)
    user.save(update_fields=['avon_points'])
    txn.status      = 'approved'
    txn.description = txn.description + ' [Admin approved]'
    txn.save(update_fields=['status', 'description'])
    try:
        send_mail(
            subject='Withdrawal Approved ✓ — T&TG Trade Corp',
            message=(
                f'Hi {user.first_name or user.username},\n\n'
                f'Your withdrawal of {txn.points} points has been approved.\n'
                f'Payment will be processed on the scheduled date.\n\nT&TG Trade Corp'
            ),
            from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
            recipient_list=[user.email], fail_silently=True,
        )
    except Exception:
        pass
    messages.success(request, f'Withdrawal #{pk} approved. {txn.points} points deducted from {user.username}.')
    return redirect(request.META.get('HTTP_REFERER', '/accounts/dashboard/#notifications'))


@staff_member_required
def reject_withdrawal(request, pk):
    from accounts.models import AvonPointTransaction
    from django.shortcuts import get_object_or_404
    from django.core.mail import send_mail
    from django.conf import settings as djsettings
    txn    = get_object_or_404(AvonPointTransaction, pk=pk, status='pending_approval')
    reason = request.POST.get('reason', 'Rejected by admin.')
    txn.status      = 'rejected'
    txn.description = txn.description + f' [Rejected: {reason}]'
    txn.save(update_fields=['status', 'description'])
    try:
        user = txn.user
        send_mail(
            subject='Withdrawal Declined — T&TG Trade Corp',
            message=(
                f'Hi {user.first_name or user.username},\n\n'
                f'Your withdrawal of {txn.points} points was declined.\n'
                f'Reason: {reason}\n'
                f'Your balance has NOT been affected.\n\nT&TG Trade Corp'
            ),
            from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
            recipient_list=[user.email], fail_silently=True,
        )
    except Exception:
        pass
    messages.warning(request, f'Withdrawal #{pk} rejected. No points deducted.')
    return redirect(request.META.get('HTTP_REFERER', '/accounts/dashboard/#notifications'))


def blog_list(request):
    from .models import BlogPost
    posts    = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    featured = posts.filter(is_featured=True).first()
    ctx = {'posts': posts, 'featured': featured}
    return render(request, 'core/blog_list.html', ctx)


def blog_detail(request, slug):
    from .models import BlogPost
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views_count += 1
    post.save(update_fields=['views_count'])
    related = BlogPost.objects.filter(
        is_published=True, category=post.category
    ).exclude(pk=post.pk)[:3]
    return render(request, 'core/blog_detail.html', {'post': post, 'related': related})


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def terms(request):
    return render(request, 'core/terms.html')


def faq(request):
    faqs = {
        "☕ About Our Coffee": [
            ("What types of coffee does T&TG sell?",
             "T&TG Arabica Green Coffee ($35/kg) — smooth high-altitude beans from Uganda; and T&TG Robusta Green Coffee ($28/kg) — bold beans ideal for espresso blends and commercial roasters."),
            ("Where is the coffee sourced?",
             "All T&TG coffee is sourced directly from Uganda, East Africa. Our supply chain is CFIA-certified and traceable from farm to port."),
            ("What is the minimum order quantity?",
             "You can order as little as 1 kg. For bulk and export orders (25kg+), contact tom.grouptrade@gmail.com for pricing."),
        ],
        "🛒 Orders & Shopping": [
            ("How do I place an order?",
             "Browse products, add to cart, then sign in to complete checkout. You can also click Buy Now on any product page."),
            ("Can I cancel my order?",
             "Under the Ontario Consumer Protection Act 2002, you have a 7-day right to cancel. Email tom.grouptrade@gmail.com with your order number within 7 days."),
            ("How do I track my order?",
             "Log in and go to My Account → My Orders to see live order status updates."),
        ],
        "🚚 Shipping & Delivery": [
            ("Which countries do you ship to?",
             "Canada, Uganda, Kenya and USA (Ohio). Contact us for other destinations."),
            ("How long does delivery take?",
             "Canada: 5–10 business days. USA/Ohio: 7–14 days. Uganda/Kenya: 14–21 days. Customs clearance may add time for international orders."),
            ("Who pays import duties?",
             "The buyer is responsible for import duties and taxes in their destination country."),
        ],
        "💰 Loyalty Points": [
            ("How do I earn loyalty points?",
             "You earn 0.5% of your order value as loyalty points on every purchase. Referred purchases earn at 1%."),
            ("When can I withdraw?",
             "Day 45 after a qualifying purchase. Withdrawals require admin approval and your 4-digit security PIN."),
        ],
        "💳 Payments": [
            ("What payment methods are accepted?",
             "Credit/debit cards (Stripe) and mobile money (Flutterwave). T&TG never stores card details."),
        ],
        "🔒 Account & Security": [
            ("How do I reset my password?",
             "Click Forgot password on the Sign In page. A reset link will be sent to your registered email (valid 24 hours)."),
            ("Why is my account locked?",
             "Accounts lock for 30 minutes after 5 failed login attempts. Email tom.grouptrade@gmail.com for urgent help."),
        ],
    }
    return render(request, 'core/faq.html', {'faqs': faqs})


def newsletter_subscribe(request):
    from .models import NewsletterSubscriber
    from django.http import JsonResponse
    if request.method == 'POST':
        email   = request.POST.get('email','').strip()
        name    = request.POST.get('name','').strip()
        consent = request.POST.get('consent','') == 'on'
        if not consent:
            messages.error(request, 'Please confirm your consent to subscribe.')
        elif email:
            sub, created = NewsletterSubscriber.objects.get_or_create(
                email=email, defaults={'name': name, 'consent': True}
            )
            if created:
                messages.success(request,
                    f'✅ Subscribed! Thank you {name or ""}. '
                    f'You can unsubscribe at any time via email to tom.grouptrade@gmail.com.')
            else:
                messages.info(request, 'You are already subscribed to T&TG updates.')
    return redirect(request.META.get('HTTP_REFERER', reverse('home')))
