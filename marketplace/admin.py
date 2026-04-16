from django.contrib import admin
from .models import Product, Order, ProductReview

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'currency', 'quantity_available', 'market_type', 'is_active', 'is_featured']
    list_filter = ['category', 'market_type', 'is_active', 'is_featured']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'product', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'order_type', 'delivery_type']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
