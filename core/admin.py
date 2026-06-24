from django.contrib import admin
from .models import Notification, LoyaltySettings, BlogPost


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['title', 'notif_type', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    actions       = ['mark_read']

    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_read.short_description = "Mark selected as read"


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(admin.ModelAdmin):
    list_display = ['consumer_rate_display', 'referral_rate_display', 'payment_days', 'updated_at']
    fieldsets = (
        ('T&TG Trade Loyalty Platform — Rate Configuration', {
            'description': (
                'These rates are applied automatically on every purchase. '
                'Changes take effect immediately for all new orders.'
            ),
            'fields': ('consumer_rate', 'referral_rate', 'payment_days'),
        }),
    )

    def consumer_rate_display(self, obj):
        return f"{float(obj.consumer_rate)*100:.2f}% (Consumer)"
    consumer_rate_display.short_description = 'Consumer Rate'

    def referral_rate_display(self, obj):
        return f"{float(obj.referral_rate)*100:.2f}% (Referral)"
    referral_rate_display.short_description = 'Referral Rate'

    def has_add_permission(self, request):
        # Only one settings row allowed
        return not LoyaltySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'author', 'is_published', 'is_featured', 'views_count', 'published_at')
    list_filter   = ('is_published', 'is_featured', 'category')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_featured')
    ordering      = ('-published_at', '-created_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'author')}),
        ('Content', {'fields': ('excerpt', 'content')}),
        ('Cover Image', {'fields': ('cover_image', 'cover_image_url')}),
        ('Publishing', {'fields': ('is_published', 'is_featured', 'published_at')}),
    )
