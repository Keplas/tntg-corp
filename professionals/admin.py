from django.contrib import admin
from .models import Department, ProfessionalProfile, ServicePackage, ServiceBooking


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'icon', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'title', 'department', 'years_experience', 'is_available']
    list_editable = ['is_available']
    list_filter   = ['department', 'is_available']
    search_fields = ['full_name', 'title']


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display  = ['name', 'department', 'service_type', 'price', 'currency', 'is_active', 'is_featured', 'order']
    list_editable = ['price', 'is_active', 'is_featured', 'order']
    list_filter   = ['department', 'service_type', 'is_active']
    search_fields = ['name']


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display  = ['ref', 'full_name', 'package', 'client_type', 'payment_status', 'status', 'professional', 'created_at']
    list_editable = ['status', 'professional']
    list_filter   = ['status', 'payment_status', 'client_type', 'package__department']
    search_fields = ['full_name', 'email', 'company_name', 'moneris_order_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at', 'amount', 'currency', 'moneris_order_id']
    fieldsets = (
        ('Service',  {'fields': ('package', 'professional', 'status', 'hq_notes')}),
        ('Client',   {'fields': ('client_type', 'full_name', 'email', 'phone', 'company_name')}),
        ('Request',  {'fields': ('problem_description', 'urgency')}),
        ('Payment',  {'fields': ('amount', 'currency', 'payment_status', 'moneris_order_id', 'paid_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def ref(self, obj):
        return obj.ref()
    ref.short_description = 'Ref'
