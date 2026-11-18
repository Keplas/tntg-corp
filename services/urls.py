from django.urls import path
from . import views

urlpatterns = [
    path('', views.trade_ecommerce, name='trade_ecommerce'),
    path('join/', views.join_program, name='join_program'),
    path('financial/insurance/', views.insurance, name='insurance'),
    path('financial/brokerage/', views.brokerage, name='brokerage'),
    path('cooperation-program/', views.cooperation_program, name='cooperation_program'),
    path('import-export/', views.import_export, name='import_export'),
    path('forex/', views.forex, name='forex'),
    # Partnership
    path('partnership/apply/', views.partnership_apply, name='partnership_apply'),
    # Franchise patterns live in franchise_urls.py — included at /franchise/ in tntg_corp/urls.py
]
