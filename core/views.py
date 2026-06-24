from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from marketplace.models import Product
from training.models import TrainingProgram, TVProgram
from services.models import ContactInquiry, ForexRate
from .models import Notification, LoyaltySettings, BlogPost

OPERATION_COUNTRIES = [
    {'code': 'CA', 'name': 'Canada', 'flag': '🇨🇦'},
    {'code': 'UG', 'name': 'Uganda', 'flag': '🇺🇬'},
    {'code': 'KE', 'name': 'Kenya',  'flag': '🇰🇪'},
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
    # Notifications now live as a section within the Analytics Dashboard —
    # redirect old links/bookmarks straight there.
    return redirect(reverse('analytics_dashboard') + '#notifications')


@staff_member_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.is_read = True
    notif.save()
    return redirect(notif.link or (reverse('analytics_dashboard') + '#notifications'))


@staff_member_required
def mark_all_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect(reverse('analytics_dashboard') + '#notifications')


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

    # Notifications — now surfaced as a section within this dashboard
    # rather than a separate top-level page (see notifications() below).
    notifs       = Notification.objects.all()[:100]
    unread_count = Notification.objects.filter(is_read=False).count()

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
        'notifs': notifs,
        'unread_count': unread_count,
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


# ── Blog / News ────────────────────────────────────────────────────────────────

def blog_list(request):
    """Blog & News listing — filterable by category."""
    category = request.GET.get('category', '')
    posts = BlogPost.objects.filter(is_published=True)
    if category:
        posts = posts.filter(category=category)

    featured  = BlogPost.objects.filter(is_published=True, is_featured=True).first()
    categories = BlogPost.CATEGORY_CHOICES

    # Simple manual pagination (10 per page)
    from django.core.paginator import Paginator
    paginator  = Paginator(posts, 9)
    page_num   = request.GET.get('page', 1)
    page_obj   = paginator.get_page(page_num)

    return render(request, 'core/blog_list.html', {
        'page_obj':   page_obj,
        'featured':   featured,
        'categories': categories,
        'current_cat': category,
    })


def blog_detail(request, slug):
    """Single blog post."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Increment view count
    BlogPost.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)

    related = BlogPost.objects.filter(
        is_published=True, category=post.category
    ).exclude(pk=post.pk)[:3]

    return render(request, 'core/blog_detail.html', {
        'post':    post,
        'related': related,
    })
