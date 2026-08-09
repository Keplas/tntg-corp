from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, ProductReview, ProductCountryPrice


class CountryPriceInline(admin.TabularInline):
    model       = ProductCountryPrice
    extra       = 6
    fields      = ['country','price','currency','is_active']
    max_num     = 6


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [CountryPriceInline]
    list_display  = ['image_preview', 'name', 'category', 'price',
                     'currency', 'quantity_available', 'market_type', 'is_active', 'is_featured']
    list_filter   = ['category', 'market_type', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active', 'is_featured']
    fields = [
        'name', 'category', 'description', 'price', 'currency',
        'quantity_available', 'unit', 'market_type', 'seller',
        'origin_country', 'image', 'image_url', 'video_url', 'is_active', 'is_featured',
    ]

    def image_preview(self, obj):
        url = None
        if obj.image:
            try:
                url = obj.image.url
            except Exception:
                pass
        if not url:
            url = getattr(obj, 'image_url', None)
        if url:
            return format_html(
                '<img src="{}" style="width:56px;height:56px;object-fit:cover;border-radius:8px">',
                url
            )
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


@admin.register(ProductCountryPrice)
class ProductCountryPriceAdmin(admin.ModelAdmin):
    list_display  = ['product', 'country', 'currency', 'price', 'is_active', 'updated_at']
    list_filter   = ['country', 'currency', 'is_active']
    list_editable = ['price', 'currency', 'is_active']
    search_fields = ['product__name']
