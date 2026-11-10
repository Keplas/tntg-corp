from django.contrib import admin
from .models import InsurancePolicy, BrokerageAccount, ForexRate, ContactInquiry

admin.site.register(InsurancePolicy)
admin.site.register(BrokerageAccount)
admin.site.register(ForexRate)

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'inquiry_type', 'subject', 'is_read', 'created_at']
    list_filter = ['inquiry_type', 'is_read']

from .models import TradeInquiry

@admin.register(TradeInquiry)
class TradeInquiryAdmin(admin.ModelAdmin):
    list_display  = ['full_name','company_name','direction','coffee_type','quantity_kg','country','status','created_at']
    list_filter   = ['direction','status','business_type','coffee_type']
    list_editable = ['status']
    search_fields = ['full_name','company_name','email','country']
    readonly_fields = ['created_at','updated_at']
    fieldsets = (
        ('Client', {'fields': ('full_name','company_name','business_type','email','phone','country','user')}),
        ('Trade Details', {'fields': ('direction','origin_country','destination_country','coffee_type','quantity_kg','frequency','notes')}),
        ('Admin', {'fields': ('status','admin_notes','created_at','updated_at')}),
    )

from .models import FranchiseApplication

@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    list_display  = ['ref', 'full_name', 'email', 'franchise_type', 'investment_budget', 'country', 'status', 'created_at']
    list_filter   = ['franchise_type', 'status', 'investment_budget', 'start_timeline']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'company_name', 'country', 'proposed_location']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Applicant', {'fields': ('full_name', 'email', 'phone', 'country', 'city', 'company_name', 'user')}),
        ('Franchise Details', {'fields': ('franchise_type', 'investment_budget', 'business_experience', 'proposed_location', 'start_timeline', 'why_tntg', 'additional_notes', 'casl_consent')}),
        ('Admin', {'fields': ('status', 'admin_notes', 'created_at', 'updated_at')}),
    )

from .models import FranchiseeProfile

@admin.register(FranchiseeProfile)
class FranchiseeProfileAdmin(admin.ModelAdmin):
    list_display   = ['ref', 'display_name', 'franchise_type', 'territory', 'country', 'operational_status', 'approved_at']
    list_filter    = ['franchise_type', 'operational_status', 'country']
    list_editable  = ['operational_status']
    search_fields  = ['user__username', 'user__email', 'business_name', 'territory', 'country']
    readonly_fields = ['approved_at', 'updated_at']
    fieldsets = (
        ('Identity', {'fields': ('user', 'application', 'franchise_type', 'business_name', 'photo')}),
        ('Territory', {'fields': ('territory', 'zone', 'country')}),
        ('Status', {'fields': ('operational_status', 'hq_notes')}),
        ('Timestamps', {'fields': ('approved_at', 'updated_at')}),
    )

from .models import FranchiseeProduct, FranchiseeOrder, StockRequest

@admin.register(FranchiseeProduct)
class FranchiseeProductAdmin(admin.ModelAdmin):
    list_display   = ['sku', 'name', 'franchisee', 'category', 'selling_price', 'stock_qty', 'status', 'added_at']
    list_filter    = ['status', 'category']
    list_editable  = ['status']
    search_fields  = ['sku', 'name', 'franchisee__business_name']
    readonly_fields = ['added_at', 'updated_at']

@admin.register(FranchiseeOrder)
class FranchiseeOrderAdmin(admin.ModelAdmin):
    list_display   = ['ref', 'franchisee', 'customer_name', 'product_name', 'quantity', 'total', 'status', 'placed_at']
    list_filter    = ['status']
    list_editable  = ['status']
    search_fields  = ['customer_name', 'customer_email', 'product_name']
    readonly_fields = ['placed_at', 'updated_at']

@admin.register(StockRequest)
class StockRequestAdmin(admin.ModelAdmin):
    list_display   = ['ref', 'franchisee', 'product_name', 'quantity_requested', 'urgency', 'status', 'submitted_at']
    list_filter    = ['status', 'urgency']
    list_editable  = ['status']
    search_fields  = ['product_name', 'franchisee__business_name']
    readonly_fields = ['created_at', 'updated_at']

from .models import PartnershipApplication

@admin.register(PartnershipApplication)
class PartnershipApplicationAdmin(admin.ModelAdmin):
    list_display  = ['ref', 'full_name', 'email', 'partnership_type', 'country', 'annual_capacity', 'status', 'created_at']
    list_filter   = ['partnership_type', 'status', 'annual_capacity', 'start_timeline']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'company_name', 'country', 'city']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Applicant', {'fields': ('full_name', 'email', 'phone', 'country', 'city', 'company_name', 'user')}),
        ('Partnership Details', {'fields': ('partnership_type', 'company_description', 'what_you_offer', 'annual_capacity', 'start_timeline', 'why_tntg', 'additional_notes', 'casl_consent')}),
        ('Admin', {'fields': ('status', 'admin_notes', 'created_at', 'updated_at')}),
    )
