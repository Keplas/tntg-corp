"""
B2B Referral Platform views — Authorized Resellers
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count


# ── Public landing ────────────────────────────────────────────────────────────

def b2b_landing(request):
    """B2B Referral Platform marketing page."""
    return render(request, 'services/b2b_landing.html', {
        'page': 'b2b',
    })


# ── Application ───────────────────────────────────────────────────────────────

def b2b_apply(request):
    """Public B2B partner application form."""
    from .models import B2BApplication
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            app = B2BApplication.objects.create(
                full_name              = d.get('full_name', '').strip(),
                email                  = d.get('email', '').strip(),
                phone                  = d.get('phone', '').strip(),
                country                = d.get('country', '').strip(),
                city                   = d.get('city', '').strip(),
                company_name           = d.get('company_name', '').strip(),
                business_type          = d.get('business_type', 'small_business'),
                store_type             = d.get('store_type', 'physical'),
                store_address          = d.get('store_address', '').strip(),
                website                = d.get('website', '').strip(),
                monthly_order_estimate = d.get('monthly_order_estimate', 'under_500'),
                years_in_business      = d.get('years_in_business', 'none'),
                products_interest      = d.get('products_interest', '').strip(),
                why_partner            = d.get('why_partner', '').strip(),
                additional_notes       = d.get('additional_notes', '').strip(),
                casl_consent           = d.get('casl_consent') == 'on',
                user                   = request.user if request.user.is_authenticated else None,
            )
        except Exception as e:
            messages.error(request, f'Submission failed: {e}. Please try again or contact tom.grouptrade@gmail.com.')
            return redirect('b2b_apply')

        # Notify admin
        try:
            send_mail(
                subject=f'New B2B Reseller Application #{app.ref()} — {app.full_name}',
                message=(
                    f'New B2B RESELLER APPLICATION received:\n\n'
                    f'Name:          {app.full_name}\n'
                    f'Company:       {app.company_name or "N/A"}\n'
                    f'Email:         {app.email}\n'
                    f'Phone:         {app.phone or "N/A"}\n'
                    f'Country:       {app.country}\n'
                    f'City:          {app.city or "N/A"}\n\n'
                    f'Business Type: {app.get_business_type_display()}\n'
                    f'Store Type:    {app.get_store_type_display()}\n'
                    f'Store Address: {app.store_address or "N/A"}\n'
                    f'Website:       {app.website or "N/A"}\n\n'
                    f'Monthly Order: {app.get_monthly_order_estimate_display()}\n'
                    f'Experience:    {app.get_years_in_business_display()}\n\n'
                    f'Products Interest:\n{app.products_interest}\n\n'
                    f'Why Partner:\n{app.why_partner}\n\n'
                    f'Notes: {app.additional_notes or "None"}\n'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request,
            f'Application #{app.ref()} submitted! Our team will review it within 3 business days.')
        return redirect('b2b_apply_success')

    return render(request, 'services/b2b_apply.html', {
        'prefill': {
            'full_name':  request.user.get_full_name() if request.user.is_authenticated else '',
            'email':      request.user.email if request.user.is_authenticated else '',
            'phone':      getattr(request.user, 'phone', '') if request.user.is_authenticated else '',
            'country':    getattr(request.user, 'country', '') if request.user.is_authenticated else '',
            'city':       getattr(request.user, 'city', '') if request.user.is_authenticated else '',
        },
    })


def b2b_apply_success(request):
    return render(request, 'services/b2b_apply_success.html')


# ── Referral tracking ─────────────────────────────────────────────────────────

def b2b_referral_track(request, code):
    """
    Store referral code in session and redirect to marketplace.
    Every purchase made in the same session is attributed to this reseller.
    """
    from .models import B2BProfile
    try:
        profile = B2BProfile.objects.get(referral_code=code, status='active')
        request.session['b2b_ref_code'] = code
        request.session['b2b_ref_id']   = profile.pk
        request.session.modified = True
    except B2BProfile.DoesNotExist:
        pass
    return redirect('marketplace')


# ── Reseller portal ───────────────────────────────────────────────────────────

@login_required
def b2b_portal(request):
    """Personal B2B reseller dashboard."""
    from .models import B2BProfile, B2BReferral

    try:
        profile = request.user.b2b_profile
    except Exception:
        messages.info(request, 'You are not yet an Authorized Reseller. Apply below.')
        return redirect('b2b_apply')

    referrals = B2BReferral.objects.filter(reseller=profile)
    confirmed = referrals.filter(status__in=['confirmed', 'paid'])
    pending   = referrals.filter(status='pending')

    total_commission = confirmed.aggregate(total=Sum('commission'))['total'] or 0
    pending_commission = pending.aggregate(total=Sum('commission'))['total'] or 0

    ctx = {
        'profile':            profile,
        'referrals':          referrals[:30],
        'total_commission':   total_commission,
        'pending_commission': pending_commission,
        'referral_count':     referrals.count(),
        'confirmed_count':    confirmed.count(),
        'referral_url':       profile.referral_url(request),
    }
    return render(request, 'services/b2b_portal.html', ctx)


@login_required
def b2b_my_applications(request):
    """List this user's B2B applications."""
    from .models import B2BApplication
    apps = B2BApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/b2b_my_applications.html', {'applications': apps})


# ════════════════════════════════════════════════════════════════════════════════
# RESELLER — WHOLESALE DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def reseller_dashboard(request):
    """Reseller wholesale dashboard — orders, private pricing, catalog."""
    from .models import B2BProfile, ResellerBulkOrder, ResellerPricing
    from decimal import Decimal

    try:
        profile = request.user.b2b_profile
    except Exception:
        messages.info(request, 'You need an Authorized Reseller account to access this area.')
        return redirect('b2b_apply')

    if profile.status != 'active':
        messages.warning(request, 'Your reseller account is currently suspended. Contact support.')
        return redirect('b2b_landing')

    disc = Decimal(str(profile.wholesale_discount_pct)) / 100

    # Recent bulk orders
    orders = ResellerBulkOrder.objects.filter(reseller=profile).order_by('-created_at')[:10]

    # Private pricing entries
    my_prices = {rp.product_id: rp for rp in
                 ResellerPricing.objects.filter(reseller=profile).select_related('product')}

    ctx = {
        'profile':    profile,
        'orders':     orders,
        'my_prices':  my_prices,
        'disc':       profile.wholesale_discount_pct,
        'order_count': ResellerBulkOrder.objects.filter(reseller=profile).count(),
        'active_count': ResellerBulkOrder.objects.filter(
            reseller=profile, status__in=['confirmed','processing','shipped']).count(),
        'page': 'reseller_dashboard',
    }
    return render(request, 'services/reseller_dashboard.html', ctx)


@login_required
def reseller_catalog(request):
    """Browse T&TG products at wholesale prices."""
    from .models import B2BProfile, ResellerPricing
    from marketplace.models import Product
    from decimal import Decimal

    try:
        profile = request.user.b2b_profile
    except Exception:
        return redirect('b2b_apply')

    disc = Decimal(str(profile.wholesale_discount_pct)) / 100
    products = Product.objects.filter(is_active=True).order_by('category', 'name')

    my_prices = {rp.product_id: rp for rp in
                 ResellerPricing.objects.filter(reseller=profile).select_related('product')}

    # Attach wholesale price to each product object
    for p in products:
        p.ws_price = round(p.price * (1 - disc), 2)
        p.my_pricing = my_prices.get(p.pk)

    ctx = {
        'profile':  profile,
        'products': products,
        'disc':     profile.wholesale_discount_pct,
        'page':     'reseller_catalog',
    }
    return render(request, 'services/reseller_catalog.html', ctx)


@login_required
def reseller_set_price(request, product_pk):
    """AJAX: set/update private selling price for a product."""
    from .models import B2BProfile, ResellerPricing
    from marketplace.models import Product
    from django.http import JsonResponse
    from decimal import Decimal, InvalidOperation

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)

    try:
        profile = request.user.b2b_profile
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Not a reseller'}, status=403)

    product = get_object_or_404(Product, pk=product_pk)
    raw = request.POST.get('sell_price', '').strip()
    notes = request.POST.get('notes', '').strip()[:255]

    try:
        price = Decimal(raw)
        if price <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid price'}, status=400)

    disc = Decimal(str(profile.wholesale_discount_pct)) / 100
    ws_price = product.price * (1 - disc)
    if price < ws_price:
        return JsonResponse({'ok': False,
            'error': f'Selling price must be at least your wholesale cost (USD {ws_price:.2f})'}, status=400)

    rp, _ = ResellerPricing.objects.update_or_create(
        reseller=profile, product=product,
        defaults={'sell_price': price, 'currency': product.currency or 'USD', 'notes': notes}
    )
    return JsonResponse({'ok': True, 'sell_price': str(rp.sell_price),
                         'margin': str(rp.margin())})


@login_required
def reseller_place_order(request):
    """Create a new bulk order (draft) or add items to existing draft."""
    from .models import B2BProfile, ResellerBulkOrder, ResellerBulkOrderItem
    from marketplace.models import Product
    from django.http import JsonResponse

    if request.method != 'POST':
        return redirect('reseller_catalog')

    try:
        profile = request.user.b2b_profile
    except Exception:
        return redirect('b2b_apply')

    product_pk = request.POST.get('product_pk')
    quantity   = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, pk=product_pk)

    # Get or create a draft order
    draft = ResellerBulkOrder.objects.filter(reseller=profile, status='draft').first()
    if not draft:
        draft = ResellerBulkOrder.objects.create(reseller=profile)

    item, created = ResellerBulkOrderItem.objects.get_or_create(
        order=draft, product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    draft.recalculate_total()
    messages.success(request, f'{product.name} × {quantity} added to your draft order.')
    return redirect('reseller_catalog')


@login_required
def reseller_order_detail(request, ref):
    """View / submit a bulk order."""
    from .models import B2BProfile, ResellerBulkOrder
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    try:
        profile = request.user.b2b_profile
    except Exception:
        return redirect('b2b_apply')

    order = get_object_or_404(ResellerBulkOrder, ref=ref, reseller=profile)

    if request.method == 'POST' and order.status == 'draft':
        order.notes = request.POST.get('notes', '')
        order.status = 'submitted'
        order.save()
        # Notify admin
        try:
            send_mail(
                subject=f'New Wholesale Order {order.ref} — {profile.store_name}',
                message=(
                    f'Reseller: {profile.store_name}\n'
                    f'Order: {order.ref}\n'
                    f'Total: USD {order.total_usd}\n'
                    f'Items:\n' +
                    '\n'.join(f'  - {i.product.name} × {i.quantity} @ USD {i.unit_price()}'
                              for i in order.items.select_related('product').all()) +
                    f'\n\nNotes: {order.notes or "None"}'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(request, f'Order {order.ref} submitted! T&TG will confirm it shortly.')
        return redirect('reseller_dashboard')

    ctx = {
        'profile': profile,
        'order':   order,
        'items':   order.items.select_related('product').all(),
        'page':    'reseller_dashboard',
    }
    return render(request, 'services/reseller_order_detail.html', ctx)


# ════════════════════════════════════════════════════════════════════════════════
# SUPPLIERS
# ════════════════════════════════════════════════════════════════════════════════

def supplier_register(request):
    """Register as a supplier (public form)."""
    from .models import SupplierProfile
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            profile = SupplierProfile.objects.create(
                user            = request.user if request.user.is_authenticated else None,
                full_name       = d.get('full_name', '').strip(),
                email           = d.get('email', '').strip(),
                phone           = d.get('phone', '').strip(),
                country         = d.get('country', '').strip(),
                city            = d.get('city', '').strip(),
                company_name    = d.get('company_name', '').strip(),
                supplier_type   = d.get('supplier_type', 'individual'),
                products_supply = d.get('products_supply', '').strip(),
            )
        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            return redirect('supplier_register')

        try:
            send_mail(
                subject=f'New Supplier Registration {profile.ref()} — {profile.full_name}',
                message=(
                    f'New supplier registered:\n\n'
                    f'Name:    {profile.full_name}\n'
                    f'Company: {profile.company_name or "N/A"}\n'
                    f'Type:    {profile.get_supplier_type_display()}\n'
                    f'Country: {profile.country}\n'
                    f'Email:   {profile.email}\n'
                    f'Phone:   {profile.phone or "N/A"}\n\n'
                    f'Products: {profile.products_supply}'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Registration submitted! You can now log in and submit deals.')
        if request.user.is_authenticated:
            return redirect('supplier_portal')
        return redirect('b2b_landing')

    prefill = {}
    if request.user.is_authenticated:
        u = request.user
        prefill = {
            'full_name': u.get_full_name(),
            'email':     u.email,
            'phone':     getattr(u, 'phone', ''),
            'country':   getattr(u, 'country', ''),
            'city':      getattr(u, 'city', ''),
        }
    return render(request, 'services/supplier_register.html', {'prefill': prefill})


@login_required
def supplier_portal(request):
    """Supplier dashboard — submit and track deals."""
    from .models import SupplierProfile, SupplierDeal

    try:
        profile = request.user.supplier_profile
    except Exception:
        messages.info(request, 'Please register as a supplier first.')
        return redirect('supplier_register')

    deals = SupplierDeal.objects.filter(supplier=profile).order_by('-created_at')
    ctx = {
        'profile':  profile,
        'deals':    deals,
        'pending':  deals.filter(status__in=['draft','submitted','reviewing']).count(),
        'approved': deals.filter(status='approved').count(),
        'page':     'supplier_portal',
    }
    return render(request, 'services/supplier_portal.html', ctx)


@login_required
def supplier_submit_deal(request):
    """Submit a new supplier deal with documents."""
    from .models import SupplierProfile, SupplierDeal
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    try:
        profile = request.user.supplier_profile
    except Exception:
        return redirect('supplier_register')

    if request.method == 'POST':
        d = request.POST
        f = request.FILES
        try:
            deal = SupplierDeal(
                supplier        = profile,
                product_desc    = d.get('product_desc', '').strip(),
                quantity_kg     = d.get('quantity_kg') or None,
                agreed_price_usd= d.get('agreed_price_usd') or None,
                notes           = d.get('notes', '').strip(),
                status          = 'submitted',
            )
            if f.get('doc_application'):
                deal.doc_application = f['doc_application']
            if f.get('doc_sales_agreement'):
                deal.doc_sales_agreement = f['doc_sales_agreement']
            if f.get('doc_cargo_agreement'):
                deal.doc_cargo_agreement = f['doc_cargo_agreement']
            deal.save()
        except Exception as e:
            messages.error(request, f'Submission failed: {e}')
            return redirect('supplier_submit_deal')

        try:
            send_mail(
                subject=f'New Supplier Deal {deal.ref} — {profile.full_name}',
                message=(
                    f'Supplier: {profile.full_name} ({profile.company_name or "Individual"})\n'
                    f'Deal Ref: {deal.ref}\n'
                    f'Product:  {deal.product_desc}\n'
                    f'Quantity: {deal.quantity_kg or "N/A"} kg\n'
                    f'Value:    {deal.agreed_price_usd or "N/A"} USD\n\n'
                    f'Docs: Application={bool(deal.doc_application)}, '
                    f'Sales Agreement={bool(deal.doc_sales_agreement)}, '
                    f'Cargo={bool(deal.doc_cargo_agreement)}\n\n'
                    f'Notes: {deal.notes or "None"}'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f'Deal {deal.ref} submitted successfully.')
        return redirect('supplier_portal')

    return render(request, 'services/supplier_submit_deal.html', {
        'profile': profile,
        'page':    'supplier_portal',
    })


# ════════════════════════════════════════════════════════════════════════════════
# SHIPPING COMPANIES
# ════════════════════════════════════════════════════════════════════════════════

def shipping_register(request):
    """Register as a shipping / cargo company (public form)."""
    from .models import ShippingCompany
    from django.core.mail import send_mail
    from django.conf import settings as djsettings

    if request.method == 'POST':
        d = request.POST
        try:
            company = ShippingCompany.objects.create(
                user            = request.user if request.user.is_authenticated else None,
                company_name    = d.get('company_name', '').strip(),
                contact_name    = d.get('contact_name', '').strip(),
                email           = d.get('email', '').strip(),
                phone           = d.get('phone', '').strip(),
                country         = d.get('country', '').strip(),
                city            = d.get('city', '').strip(),
                registration_no = d.get('registration_no', '').strip(),
                website         = d.get('website', '').strip(),
                service_areas   = d.get('service_areas', '').strip(),
            )
        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            return redirect('shipping_register')

        try:
            send_mail(
                subject=f'New Shipping Company {company.ref()} — {company.company_name}',
                message=(
                    f'New shipping company registered:\n\n'
                    f'Company: {company.company_name}\n'
                    f'Contact: {company.contact_name}\n'
                    f'Country: {company.country}\n'
                    f'Email:   {company.email}\n'
                    f'Phone:   {company.phone or "N/A"}\n'
                    f'Reg No:  {company.registration_no or "N/A"}\n'
                    f'Areas:   {company.service_areas or "N/A"}'
                ),
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Company registered! You can now upload shipment documents.')
        if request.user.is_authenticated:
            return redirect('shipping_portal')
        return redirect('b2b_landing')

    prefill = {}
    if request.user.is_authenticated:
        u = request.user
        prefill = {
            'contact_name': u.get_full_name(),
            'email':        u.email,
            'phone':        getattr(u, 'phone', ''),
            'country':      getattr(u, 'country', ''),
        }
    return render(request, 'services/shipping_register.html', {'prefill': prefill})


@login_required
def shipping_portal(request):
    """Shipping company dashboard — upload and manage shipment docs."""
    from .models import ShippingCompany, ShipmentDoc, SupplierDeal

    try:
        company = request.user.shipping_company
    except Exception:
        messages.info(request, 'Please register your shipping company first.')
        return redirect('shipping_register')

    docs = ShipmentDoc.objects.filter(shipping_co=company).select_related(
        'supplier_deal', 'supplier_deal__supplier'
    ).order_by('-uploaded_at')

    ctx = {
        'company':  company,
        'docs':     docs,
        'page':     'shipping_portal',
    }
    return render(request, 'services/shipping_portal.html', ctx)


@login_required
def shipping_upload_doc(request):
    """Upload a shipment document."""
    from .models import ShippingCompany, ShipmentDoc, SupplierDeal

    try:
        company = request.user.shipping_company
    except Exception:
        return redirect('shipping_register')

    if request.method == 'POST':
        f    = request.FILES.get('document')
        deal_ref = request.POST.get('deal_ref', '').strip()
        doc_type = request.POST.get('doc_type', 'other')
        desc     = request.POST.get('description', '').strip()

        if not f:
            messages.error(request, 'Please select a file to upload.')
            return redirect('shipping_upload_doc')

        deal = None
        if deal_ref:
            try:
                deal = SupplierDeal.objects.get(ref=deal_ref.upper())
            except SupplierDeal.DoesNotExist:
                messages.warning(request, f'Deal reference "{deal_ref}" not found — document saved without deal link.')

        try:
            ShipmentDoc.objects.create(
                shipping_co   = company,
                supplier_deal = deal,
                doc_type      = doc_type,
                document      = f,
                description   = desc,
            )
            messages.success(request, 'Document uploaded successfully.')
        except Exception as e:
            messages.error(request, f'Upload failed: {e}')

        return redirect('shipping_portal')

    return render(request, 'services/shipping_upload_doc.html', {
        'company':  company,
        'doc_types': ShipmentDoc.DOC_TYPE_CHOICES,
        'page':     'shipping_portal',
    })
