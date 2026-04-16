from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_select, name='marketplace'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/order/', views.place_order, name='place_order'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
]
