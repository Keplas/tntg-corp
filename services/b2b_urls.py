"""
B2B Platform URL patterns — included at path('b2b/', ...) in tntg_corp/urls.py.
Covers: referral portal, reseller wholesale, supplier portal, shipping company portal.
"""
from django.urls import path
from . import b2b_views

urlpatterns = [
    # ── Public landing / application ─────────────────────────────────────────
    path('',                        b2b_views.b2b_landing,         name='b2b_landing'),
    path('apply/',                  b2b_views.b2b_apply,           name='b2b_apply'),
    path('apply/success/',          b2b_views.b2b_apply_success,   name='b2b_apply_success'),
    path('portal/',                 b2b_views.b2b_portal,          name='b2b_portal'),
    path('my-applications/',        b2b_views.b2b_my_applications, name='b2b_my_applications'),
    path('ref/<str:code>/',         b2b_views.b2b_referral_track,  name='b2b_referral_track'),

    # ── Reseller wholesale ───────────────────────────────────────────────────
    path('reseller/',               b2b_views.reseller_dashboard,  name='reseller_dashboard'),
    path('reseller/catalog/',       b2b_views.reseller_catalog,    name='reseller_catalog'),
    path('reseller/set-price/<int:product_pk>/', b2b_views.reseller_set_price, name='reseller_set_price'),
    path('reseller/order/',         b2b_views.reseller_place_order,name='reseller_place_order'),
    path('reseller/order/<str:ref>/',b2b_views.reseller_order_detail, name='reseller_order_detail'),

    # ── Supplier portal ──────────────────────────────────────────────────────
    path('supplier/register/',      b2b_views.supplier_register,   name='supplier_register'),
    path('supplier/',               b2b_views.supplier_portal,     name='supplier_portal'),
    path('supplier/submit-deal/',   b2b_views.supplier_submit_deal,name='supplier_submit_deal'),

    # ── Shipping company portal ──────────────────────────────────────────────
    path('shipping/register/',      b2b_views.shipping_register,   name='shipping_register'),
    path('shipping/',               b2b_views.shipping_portal,     name='shipping_portal'),
    path('shipping/upload/',        b2b_views.shipping_upload_doc, name='shipping_upload_doc'),
]
