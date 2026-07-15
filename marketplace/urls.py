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
    path('orders/<int:pk>/pay/success/',views.payment_success,     name='payment_success'),
    path('cart/',                      views.cart_view,        name='cart'),
    path('cart/add/<int:pk>/',         views.cart_add,         name='cart_add'),
    path('cart/remove/<int:pk>/',      views.cart_remove,      name='cart_remove'),
    path('cart/update/<int:pk>/',      views.cart_update,      name='cart_update'),
    path('products/<int:pk>/review/',  views.submit_review,    name='submit_review'),
    path('products/<int:pk>/wishlist/',views.wishlist_toggle,  name='wishlist_toggle'),
    path('wishlist/',                  views.wishlist_view,    name='wishlist'),
]
