from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AvonPointTransaction


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'unique_id', 'email', 'country', 'market_type', 'avon_points', 'is_verified']
    list_filter  = ['country', 'market_type', 'is_verified', 'is_partner']
    fieldsets    = UserAdmin.fieldsets + (
        ('T&TG Profile', {'fields': (
            'unique_id', 'phone', 'country', 'city', 'address',
            'market_type', 'user_role', 'term_preference', 'business_description',
            'is_partner', 'partner_company', 'partner_id',
            'has_certificate', 'is_registered_company',
            'avon_points', 'is_verified',
            'profile_photo', 'national_id_front', 'national_id_back', 'selfie', 'declaration',
            'bio', 'profile_link', 'website',
        )}),
    )


@admin.register(AvonPointTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'transaction_type', 'points', 'status', 'min_execution_date', 'created_at']
    list_filter   = ['transaction_type', 'status', 'quarter']
    list_editable = ['status']
    search_fields = ['user__username', 'user__unique_id']

from .models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display  = ['user','cad_balance','usd_balance','ugx_balance','kes_balance','eur_balance','jpy_balance','updated_at']
    search_fields = ['user__username','user__email']
    readonly_fields = ['created_at','updated_at']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display  = ['wallet','currency','amount','transaction_type','reference','created_at']
    list_filter   = ['transaction_type','currency']
    search_fields = ['wallet__user__username','reference']
    readonly_fields = ['created_at']
