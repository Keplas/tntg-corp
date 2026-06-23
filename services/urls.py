from django.urls import path
from . import views

urlpatterns = [
    path('', views.trade_ecommerce, name='trade_ecommerce'),
    path('import-export/', views.import_export, name='import_export'),
    path('forex/', views.forex,     name='forex'),
    # Legacy URLs — still accessible in admin, just not shown in nav
    path('insurance/', views.insurance, name='insurance'),
    path('brokerage/', views.brokerage, name='brokerage'),
]
