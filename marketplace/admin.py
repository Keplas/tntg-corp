from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['image_preview', 'name', 'category', 'gender_target', 'price',
                     'currency', 'quantity_available', 'market_type', 'is_active', 'is_featured']
    list_filter   = ['category', 'gender_target', 'market_type', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['name', 'category', 'gender_target', 'price', 'is_active', 'is_featured']
    fields = [
        'name', 'category', 'gender_target', 'description', 'price', 'currency',
        'quantity_available', 'unit', 'market_type', 'seller',
        'origin_country', 'image', 'video_url', 'is_active', 'is_featured',
    ]

    def image_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;">',
                    obj.image.url
                )
            except Exception:
                return '⚠️'
        return '—'
    image_preview.short_description = 'Image'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_upload_url'] = '/admin/upload-images/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'buyer', 'product', 'quantity', 'total_price',
                     'avon_points_earned', 'reward_payment_date', 'status', 'created_at']
    list_filter   = ['status', 'order_type', 'delivery_type']
    search_fields = ['buyer__username', 'product__name']
    readonly_fields = ['reward_payment_date', 'avon_points_earned']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
