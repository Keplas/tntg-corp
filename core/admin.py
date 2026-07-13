from django.contrib import admin
from .models import Notification, LoyaltySettings, BlogPost


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['title', 'notif_type', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    actions       = ['mark_read']

    @admin.action(description='Mark selected as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(admin.ModelAdmin):
    list_display = ['consumer_rate', 'referral_rate', 'payment_days']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display       = ['title', 'category', 'author', 'is_published', 'is_featured', 'created_at']
    list_filter        = ['category', 'is_published', 'is_featured']
    list_editable      = ['is_published', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    search_fields      = ['title', 'excerpt', 'content']
