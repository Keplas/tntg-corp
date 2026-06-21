from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_select, name='marketplace'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/order/', views.place_order, name='place_order'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    # Payments
    path('orders/<int:pk>/pay/',        views.payment_select,      name='payment_select'),
    path('orders/<int:pk>/pay/card/',   views.payment_start_card,  name='payment_start_card'),
    path('orders/<int:pk>/pay/mobile/', views.payment_start_mobile,name='payment_start_mobile'),
    path('orders/<int:pk>/pay/pending/',views.payment_pending,     name='payment_pending'),
    path('orders/<int:pk>/pay/poll/',   views.poll_payment_status, name='poll_payment_status'),
    path('orders/<int:pk>/pay/success/',views.payment_success,     name='payment_success'),
]
