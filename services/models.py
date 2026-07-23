from django.db import models
from accounts.models import CustomUser

class InsurancePolicy(models.Model):
    POLICY_TYPES = [
        ('health','Health Insurance'),
        ('trade','Trade Insurance'),
        ('cargo','Cargo Insurance'),
        ('business','Business Insurance'),
        ('life','Life Insurance'),
    ]
    STATUS = [('active','Active'),('pending','Pending'),('expired','Expired'),('cancelled','Cancelled')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='insurance_policies')
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    policy_number = models.CharField(max_length=50, unique=True)
    coverage_amount = models.DecimalField(max_digits=14, decimal_places=2)
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.policy_number} - {self.user.username}"

class BrokerageAccount(models.Model):
    ACCOUNT_TYPES = [('forex','Forex'),('stocks','Stocks'),('commodities','Commodities'),('crypto','Cryptocurrency')]
    STATUS = [('active','Active'),('pending','Pending'),('suspended','Suspended')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='brokerage_accounts')
    account_number = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=5, default='USD')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

class ForexRate(models.Model):
    from_currency = models.CharField(max_length=5)
    to_currency = models.CharField(max_length=5)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_currency}/{self.to_currency} = {self.rate}"

class ContactInquiry(models.Model):
    INQUIRY_TYPES = [('general','General'),('partnership','Partnership'),('support','Support'),('investment','Investment')]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class TradeInquiry(models.Model):

    DIRECTION_CHOICES = [
        ('import', 'Import from T&TG — Buy our coffee'),
        ('export', 'Export to T&TG — Sell coffee to us'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending Review'),
        ('reviewing', 'Under Review'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
        ('completed', 'Completed'),
    ]
    BUSINESS_TYPE_CHOICES = [
        ('registered_company', 'Registered Company'),
        ('small_business',     'Small Business / Shop'),
        ('individual',         'Individual'),
        ('organisation',       'Organisation / NGO'),
    ]
    FREQUENCY_CHOICES = [
        ('one_time',   'One-Time Shipment'),
        ('monthly',    'Monthly'),
        ('quarterly',  'Quarterly'),
        ('annually',   'Annually'),
    ]
    COFFEE_CHOICES = [
        ('arabica',   'Arabica Green Coffee'),
        ('robusta',   'Robusta Green Coffee'),
        ('both',      'Both Arabica & Robusta'),
        ('artisanal', 'Artisanal Coffee Goods'),
        ('instant',   'Instant Coffee'),
        ('soap',      'Coffee-Based Soaps'),
        ('mixed',     'Mixed / Other'),
    ]

    # Client info
    full_name      = models.CharField(max_length=200)
    company_name   = models.CharField(max_length=200, blank=True)
    business_type  = models.CharField(max_length=30, choices=BUSINESS_TYPE_CHOICES)
    email          = models.EmailField()
    phone          = models.CharField(max_length=30, blank=True)
    country        = models.CharField(max_length=100)

    # Trade details
    direction           = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    origin_country      = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)
    coffee_type         = models.CharField(max_length=20, choices=COFFEE_CHOICES)
    quantity_kg         = models.DecimalField(max_digits=10, decimal_places=2)
    frequency           = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    notes               = models.TextField(blank=True)
    casl_consent        = models.BooleanField(default=False)
    location_address    = models.TextField(blank=True, help_text='Full physical address of the applicant')
    agreement_document  = models.FileField(upload_to='trade_agreements/', null=True, blank=True, help_text='Signed agreement or supporting document')

    # Admin
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    user         = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='trade_inquiries'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Trade Inquiry'
        verbose_name_plural = 'Trade Inquiries'

    def __str__(self):
        return f"{self.full_name} — {self.get_direction_display()} — {self.status}"
