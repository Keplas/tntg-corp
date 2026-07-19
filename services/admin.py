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
