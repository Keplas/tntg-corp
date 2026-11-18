"""
Franchise URL patterns — included at path('franchise/', ...) in tntg_corp/urls.py.
Patterns here do NOT carry a 'franchise/' prefix because the include already adds it.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('',                                   views.franchise_hub,              name='franchise_hub'),
    path('register/',                          views.franchise_register,         name='franchise_register'),
    path('apply/',                             views.franchise_apply,            name='franchise_apply'),
    path('dashboard/',                         views.franchise_dashboard,        name='franchise_dashboard'),
    path('<int:pk>/status/',                   views.franchise_update_status,    name='franchise_update_status'),
    path('my-applications/',                   views.my_franchise_applications,  name='my_franchise_applications'),
    path('my-store/',                          views.franchisee_store,           name='franchisee_store'),
    # Phase 2
    path('my-products/',                       views.franchise_my_products,      name='franchise_my_products'),
    path('orders/',                            views.franchise_orders,           name='franchise_orders'),
    path('orders/<int:pk>/',                   views.franchise_order_detail,     name='franchise_order_detail'),
    path('sales-reports/',                     views.franchise_sales_reports,    name='franchise_sales_reports'),
    path('inventory/',                         views.franchise_inventory,        name='franchise_inventory'),
    # Phase 3
    path('customers/',                         views.franchise_customers,        name='franchise_customers'),
    path('customers/add/',                     views.franchise_customer_add,     name='franchise_customer_add'),
    path('customers/<int:pk>/',                views.franchise_customer_detail,  name='franchise_customer_detail'),
    path('customers/<int:pk>/edit/',           views.franchise_customer_edit,    name='franchise_customer_edit'),
]
