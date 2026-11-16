from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AvonPointTransaction

# ── Restrict /admin/ to Tom (superuser) only ─────────────────────────────────
# Any staff member can be assigned is_staff, but only the superuser (Tom) may
# access the Django admin interface.  We patch the default AdminSite in-place
# so ALL registered model admins inherit this restriction automatically.
def _superuser_only(self, request):
    return request.user.is_active and request.user.is_superuser

admin.site.__class__.has_permission = _superuser_only


# ── Proxy models so Users and Admins appear in separate admin sections ────────

class RegularUser(CustomUser):
    """Proxy — regular platform users (buyers, sellers, franchisees, etc.)."""
    class Meta:
        proxy        = True
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        app_label    = 'accounts'


class AdminUser(CustomUser):
    """Proxy — platform administrators and staff (user_role=admin/finance or is_staff/superuser)."""
    class Meta:
        proxy        = True
        verbose_name        = 'Administrator'
        verbose_name_plural = 'Administrators'
        app_label    = 'accounts'


# ── Shared fieldset for the T&TG profile block ────────────────────────────────
_TNTG_FIELDSET = ('T&TG Profile', {'fields': (
    'unique_id', 'phone', 'country', 'city', 'address',
    'market_type', 'user_role', 'term_preference', 'business_description',
    'is_partner', 'partner_company', 'partner_id',
    'avon_points', 'is_verified',
    'profile_photo', 'national_id_front', 'national_id_back', 'selfie', 'declaration',
    'bio', 'profile_link', 'website',
)})


@admin.register(RegularUser)
class RegularUserAdmin(UserAdmin):
    """Admin view for regular (non-admin) platform users."""

    list_display  = ['username', 'unique_id', 'email', 'get_full_name', 'country',
                     'user_role', 'market_type', 'avon_points', 'is_verified', 'date_joined']
    list_filter   = ['user_role', 'country', 'market_type', 'is_verified', 'is_partner']
    search_fields = ['username', 'email', 'unique_id', 'first_name', 'last_name', 'phone']
    ordering      = ['-date_joined']
    fieldsets     = UserAdmin.fieldsets + (_TNTG_FIELDSET,)

    def get_queryset(self, request):
        """Only show non-admin, non-staff users."""
        return super().get_queryset(request).filter(
            is_superuser=False,
            is_staff=False,
        ).exclude(user_role__in=['admin', 'finance'])

    def get_full_name(self, obj):
        return obj.get_full_name() or '—'
    get_full_name.short_description = 'Name'


@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    """Admin view for platform administrators and staff accounts."""

    list_display  = ['username', 'unique_id', 'email', 'get_full_name',
                     'user_role', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    list_filter   = ['user_role', 'is_staff', 'is_superuser', 'is_active', 'country']
    search_fields = ['username', 'email', 'unique_id', 'first_name', 'last_name']
    ordering      = ['-date_joined']
    fieldsets     = UserAdmin.fieldsets + (_TNTG_FIELDSET,)

    def get_queryset(self, request):
        """Only show admin/staff/superuser accounts."""
        from django.db.models import Q
        return super().get_queryset(request).filter(
            Q(is_superuser=True) | Q(is_staff=True) | Q(user_role__in=['admin', 'finance'])
        )

    def get_full_name(self, obj):
        return obj.get_full_name() or '—'
    get_full_name.short_description = 'Name'


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
