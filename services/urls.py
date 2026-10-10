from django.urls import path
from . import views

urlpatterns = [
    path('', views.trade_ecommerce, name='trade_ecommerce'),
    path('join/', views.join_program, name='join_program'),
    path('cooperation-program/', views.cooperation_program, name='cooperation_program'),
    path('import-export/', views.import_export, name='import_export'),
    path('forex/', views.forex, name='forex'),
    # Franchise
    path('franchise/apply/',                views.franchise_apply,          name='franchise_apply'),
    path('franchise/dashboard/',            views.franchise_dashboard,       name='franchise_dashboard'),
    path('franchise/<int:pk>/status/',      views.franchise_update_status,   name='franchise_update_status'),
    path('franchise/my-applications/',      views.my_franchise_applications, name='my_franchise_applications'),
]
