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


# ════════════════════════════════════════════════════════════════════════
# FRANCHISE APPLICATION
# ════════════════════════════════════════════════════════════════════════

class FranchiseApplication(models.Model):

    FRANCHISE_TYPE_CHOICES = [
        ('cafe_kiosk',       'Café / Kiosk Franchise'),
        ('distribution',     'Distribution Partner'),
        ('online_reseller',  'Online Reseller'),
        ('corporate_supply', 'Corporate & Institutional Supply'),
        ('mobile_unit',      'Mobile Coffee Unit'),
    ]
    BUDGET_CHOICES = [
        ('under_10k',    'Under $10,000 CAD'),
        ('10k_25k',      '$10,000 – $25,000 CAD'),
        ('25k_50k',      '$25,000 – $50,000 CAD'),
        ('50k_100k',     '$50,000 – $100,000 CAD'),
        ('over_100k',    'Over $100,000 CAD'),
    ]
    EXPERIENCE_CHOICES = [
        ('none',         'No prior business experience'),
        ('some',         '1–3 years in business or retail'),
        ('experienced',  '3–7 years in business or retail'),
        ('expert',       '7+ years or existing franchise owner'),
    ]
    TIMELINE_CHOICES = [
        ('asap',         'As soon as possible'),
        ('3_months',     'Within 3 months'),
        ('6_months',     'Within 6 months'),
        ('1_year',       'Within 1 year'),
        ('exploring',    'Just exploring'),
    ]
    STATUS_CHOICES = [
        ('pending',    'Pending Review'),
        ('reviewing',  'Under Review'),
        ('approved',   'Approved'),
        ('rejected',   'Rejected'),
        ('on_hold',    'On Hold'),
    ]

    # Applicant info
    full_name       = models.CharField(max_length=200)
    email           = models.EmailField()
    phone           = models.CharField(max_length=30, blank=True)
    country         = models.CharField(max_length=100)
    city            = models.CharField(max_length=100, blank=True)
    company_name    = models.CharField(max_length=200, blank=True)

    # Franchise details
    franchise_type      = models.CharField(max_length=30, choices=FRANCHISE_TYPE_CHOICES)
    investment_budget   = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    business_experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    proposed_location   = models.CharField(max_length=300, help_text='City / territory / address where you plan to operate')
    start_timeline      = models.CharField(max_length=20, choices=TIMELINE_CHOICES)
    why_tntg            = models.TextField(help_text='Why do you want to franchise with T&TG?')
    additional_notes    = models.TextField(blank=True)
    casl_consent        = models.BooleanField(default=False)

    # Admin
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    user         = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='franchise_applications'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Franchise Application'
        verbose_name_plural = 'Franchise Applications'

    def __str__(self):
        return f"{self.full_name} — {self.get_franchise_type_display()} — {self.status}"

    def ref(self):
        return f'FA-{self.pk:04d}'


# ════════════════════════════════════════════════════════════════════════
# FRANCHISEE PROFILE  — created automatically on application approval
# ════════════════════════════════════════════════════════════════════════

class FranchiseeProfile(models.Model):

    OPERATIONAL_STATUS = [
        ('setup',       'Setting Up'),
        ('active',      'Active'),
        ('paused',      'Paused'),
        ('terminated',  'Terminated'),
    ]

    # Core links
    user        = models.OneToOneField(
        'accounts.CustomUser', on_delete=models.CASCADE,
        related_name='franchisee_profile'
    )
    application = models.OneToOneField(
        FranchiseApplication, on_delete=models.PROTECT,
        related_name='franchisee_profile'
    )

    # Identity
    franchise_type   = models.CharField(max_length=30, choices=FranchiseApplication.FRANCHISE_TYPE_CHOICES)
    business_name    = models.CharField(max_length=200, blank=True,
                           help_text='Trading name e.g. "T&TG Kampala North". Leave blank to auto-generate.')
    photo            = models.URLField(blank=True, help_text='Profile photo URL')

    # Territory
    territory        = models.CharField(max_length=200,
                           help_text='Named region e.g. "Kampala North", "Toronto West"')
    zone             = models.CharField(max_length=100, blank=True,
                           help_text='Sub-division e.g. "Zone A", "Eastern Corridor"')
    country          = models.CharField(max_length=100)

    # Status
    operational_status = models.CharField(max_length=20, choices=OPERATIONAL_STATUS, default='setup')
    hq_notes           = models.TextField(blank=True, help_text='Internal notes — not visible to franchisee')

    # Timestamps
    approved_at  = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-approved_at']
        verbose_name        = 'Franchisee Profile'
        verbose_name_plural = 'Franchisee Profiles'

    def __str__(self):
        return f"{self.display_name()} — {self.territory} [{self.get_operational_status_display()}]"

    def display_name(self):
        return self.business_name or f"T&TG {self.territory}"

    def ref(self):
        return f'FP-{self.pk:04d}'

    def is_active(self):
        return self.operational_status == 'active'


# ════════════════════════════════════════════════════════════════════════
# FRANCHISE PHASE 2 — PRODUCTS / ORDERS / STOCK REQUESTS
# ════════════════════════════════════════════════════════════════════════

class FranchiseeProduct(models.Model):
    STATUS_CHOICES = [
        ('pending',      'Pending HQ Approval'),
        ('approved',     'Approved'),
        ('rejected',     'Rejected by HQ'),
        ('discontinued', 'Discontinued'),
    ]
    CATEGORY_CHOICES = [
        ('coffee_bean', 'Coffee Beans (Green)'),
        ('roasted',     'Roasted Coffee'),
        ('instant',     'Instant Coffee'),
        ('artisanal',   'Artisanal Goods'),
        ('soap',        'Coffee Soaps'),
        ('other',       'Other'),
    ]
    franchisee     = models.ForeignKey(FranchiseeProfile, on_delete=models.CASCADE, related_name='products')
    name           = models.CharField(max_length=200)
    sku            = models.CharField(max_length=50, unique=True)
    category       = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    description    = models.TextField(blank=True)
    selling_price  = models.DecimalField(max_digits=10, decimal_places=2)
    hq_cost_price  = models.DecimalField(max_digits=10, decimal_places=2,
                         help_text='HQ transfer price to franchisee')
    stock_qty      = models.PositiveIntegerField(default=0)
    low_stock_level= models.PositiveIntegerField(default=10,
                         help_text='Alert when stock falls below this')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image_url      = models.URLField(blank=True)
    hq_notes       = models.TextField(blank=True)
    added_at       = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added_at']
        verbose_name        = 'Franchisee Product'
        verbose_name_plural = 'Franchisee Products'

    def __str__(self):
        return f"{self.sku} — {self.name} [{self.franchisee}]"

    @property
    def is_low_stock(self):
        return self.stock_qty <= self.low_stock_level

    @property
    def margin(self):
        return self.selling_price - self.hq_cost_price

    @property
    def margin_pct(self):
        if self.hq_cost_price:
            return round((self.margin / self.selling_price) * 100, 1)
        return 0


class FranchiseeCustomer(models.Model):
    """CRM — customer contacts for a franchisee's territory."""
    TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business',   'Business'),
    ]
    franchisee    = models.ForeignKey(FranchiseeProfile, on_delete=models.CASCADE,
                        related_name='customers')
    full_name     = models.CharField(max_length=200)
    email         = models.EmailField(blank=True)
    phone         = models.CharField(max_length=30, blank=True)
    company_name  = models.CharField(max_length=200, blank=True)
    customer_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='individual')
    address       = models.TextField(blank=True)
    notes         = models.TextField(blank=True, help_text='Internal notes about this customer')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name        = 'Franchisee Customer'
        verbose_name_plural = 'Franchisee Customers'
        unique_together = [['franchisee', 'email']]

    def __str__(self):
        return f"{self.full_name} [{self.franchisee}]"

    @property
    def display_name(self):
        return self.company_name if self.customer_type == 'business' and self.company_name else self.full_name

    @property
    def ref(self):
        return f'CUS-{self.pk:04d}'


class FranchiseeOrder(models.Model):
    STATUS_CHOICES = [
        ('new',        'New Order'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]
    franchisee    = models.ForeignKey(FranchiseeProfile, on_delete=models.CASCADE, related_name='orders')
    # Customer
    customer_name  = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30, blank=True)
    # Line item (snapshot)
    product        = models.ForeignKey(FranchiseeProduct, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='orders')
    product_name   = models.CharField(max_length=200, help_text='Name snapshot at time of order')
    quantity       = models.PositiveIntegerField(default=1)
    unit_price     = models.DecimalField(max_digits=10, decimal_places=2)
    total          = models.DecimalField(max_digits=12, decimal_places=2)
    # Status
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes          = models.TextField(blank=True)
    placed_at      = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-placed_at']
        verbose_name        = 'Franchisee Order'
        verbose_name_plural = 'Franchisee Orders'

    def __str__(self):
        return f"ORD-{self.pk:05d} — {self.customer_name} — {self.status}"

    @property
    def ref(self):
        return f'ORD-{self.pk:05d}'


class StockRequest(models.Model):
    STATUS_CHOICES = [
        ('draft',        'Draft'),
        ('submitted',    'Submitted to HQ'),
        ('acknowledged', 'Acknowledged by HQ'),
        ('processing',   'Processing'),
        ('shipped',      'Shipped'),
        ('delivered',    'Delivered'),
        ('cancelled',    'Cancelled'),
    ]
    URGENCY_CHOICES = [
        ('standard', 'Standard (5–7 business days)'),
        ('urgent',   'Urgent (2–3 business days)'),
        ('critical', 'Critical (Next business day)'),
    ]
    franchisee         = models.ForeignKey(FranchiseeProfile, on_delete=models.CASCADE,
                             related_name='stock_requests')
    product            = models.ForeignKey(FranchiseeProduct, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='stock_requests')
    product_name       = models.CharField(max_length=200, help_text='Name snapshot')
    quantity_requested = models.PositiveIntegerField()
    urgency            = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='standard')
    notes              = models.TextField(blank=True)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    hq_notes           = models.TextField(blank=True)
    submitted_at       = models.DateTimeField(null=True, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Stock Request'
        verbose_name_plural = 'Stock Requests'

    def __str__(self):
        return f"SR-{self.pk:04d} — {self.product_name} x{self.quantity_requested} [{self.status}]"

    @property
    def ref(self):
        return f'SR-{self.pk:04d}'


# ════════════════════════════════════════════════════════════════════════
# PARTNERSHIP APPLICATION
# ════════════════════════════════════════════════════════════════════════

class PartnershipApplication(models.Model):

    PARTNERSHIP_TYPE_CHOICES = [
        ('supplier',        'Coffee Supplier / Farm'),
        ('distributor',     'Distributor / Regional Manager'),
        ('manufacturer',    'Artisanal Manufacturer / Roaster'),
        ('co_manufacturer', 'Co-Manufacturing Partner'),
        ('logistics',       'Logistics / Transportation Partner'),
        ('retail_agent',    'Retail Agent / Shop Owner'),
        ('corporate',       'Corporate / Institutional Buyer'),
        ('other',           'Other / Not Listed'),
    ]
    CAPACITY_CHOICES = [
        ('under_1t',     'Under 1 tonne / month'),
        ('1t_5t',        '1 – 5 tonnes / month'),
        ('5t_20t',       '5 – 20 tonnes / month'),
        ('20t_50t',      '20 – 50 tonnes / month'),
        ('over_50t',     'Over 50 tonnes / month'),
        ('na',           'Not applicable'),
    ]
    TIMELINE_CHOICES = [
        ('asap',        'As soon as possible'),
        ('3_months',    'Within 3 months'),
        ('6_months',    'Within 6 months'),
        ('1_year',      'Within 1 year'),
        ('exploring',   'Just exploring options'),
    ]
    STATUS_CHOICES = [
        ('pending',    'Pending Review'),
        ('reviewing',  'Under Review'),
        ('approved',   'Approved'),
        ('rejected',   'Rejected'),
        ('on_hold',    'On Hold'),
    ]

    # Contact info
    full_name       = models.CharField(max_length=200)
    email           = models.EmailField()
    phone           = models.CharField(max_length=30, blank=True)
    country         = models.CharField(max_length=100)
    city            = models.CharField(max_length=100, blank=True)
    company_name    = models.CharField(max_length=200, blank=True)

    # Partnership details
    partnership_type    = models.CharField(max_length=30, choices=PARTNERSHIP_TYPE_CHOICES)
    company_description = models.TextField(help_text='Brief description of your company or operation')
    what_you_offer      = models.TextField(help_text='What products, services or capacity you bring to T&TG')
    annual_capacity     = models.CharField(max_length=20, choices=CAPACITY_CHOICES, default='na')
    start_timeline      = models.CharField(max_length=20, choices=TIMELINE_CHOICES, default='exploring')
    why_tntg            = models.TextField(help_text='Why do you want to partner with T&TG Trade Corporation?')
    additional_notes    = models.TextField(blank=True)
    casl_consent        = models.BooleanField(default=False)

    # Admin
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    user         = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='partnership_applications'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Partnership Application'
        verbose_name_plural = 'Partnership Applications'

    def __str__(self):
        return f"{self.full_name} — {self.get_partnership_type_display()} — {self.status}"

    def ref(self):
        return f'PA-{self.pk:04d}'
