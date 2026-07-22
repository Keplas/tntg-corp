from django.urls import path
from . import views

urlpatterns = [
    path('', views.trade_ecommerce, name='trade_ecommerce'),
    path('import-export/', views.import_export, name='import_export'),
    path('forex/', views.forex,     name='forex'),
    # Legacy URLs — still accessible in admin, just not shown in nav
    path('insurance/', views.insurance, name='insurance'),
    path('brokerage/', views.brokerage, name='brokerage'),
    path('trade/apply/',            views.trade_apply,         name='trade_apply'),
    path('trade/dashboard/',        views.trade_dashboard,     name='trade_dashboard'),
    path('trade/<int:pk>/status/',  views.trade_update_status, name='trade_update_status'),
    path('trade/my-inquiries/',        views.my_trade_inquiries,  name='my_trade_inquiries'),
    path('trade/<int:pk>/detail/',     views.trade_inquiry_detail, name='trade_inquiry_detail'),
]
