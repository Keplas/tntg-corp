from django.contrib import admin
from .models import InsurancePolicy, BrokerageAccount, ForexRate, ContactInquiry

admin.site.register(InsurancePolicy)
admin.site.register(BrokerageAccount)
admin.site.register(ForexRate)

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'inquiry_type', 'subject', 'is_read', 'created_at']
    list_filter = ['inquiry_type', 'is_read']
