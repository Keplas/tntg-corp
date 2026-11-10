from django.db import models


# ════════════════════════════════════════════════════════════════════════
# DEPARTMENT
# ════════════════════════════════════════════════════════════════════════

class Department(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True)
    icon        = models.CharField(max_length=60, default='fas fa-briefcase',
                      help_text='Font Awesome class e.g. fas fa-balance-scale')
    tagline     = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('pro_department', args=[self.slug])


# ════════════════════════════════════════════════════════════════════════
# PROFESSIONAL PROFILE
# ════════════════════════════════════════════════════════════════════════

class ProfessionalProfile(models.Model):
    department       = models.ForeignKey(Department, on_delete=models.CASCADE,
                           related_name='professionals')
    full_name        = models.CharField(max_length=150)
    title            = models.CharField(max_length=150,
                           help_text='e.g. "Senior Legal Counsel", "Chartered Accountant"')
    bio              = models.TextField(blank=True)
    photo            = models.URLField(blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    is_available     = models.BooleanField(default=True)
    order            = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['department', 'order', 'full_name']

    def __str__(self):
        return f'{self.full_name} — {self.department}'


# ════════════════════════════════════════════════════════════════════════
# SERVICE PACKAGE
# ════════════════════════════════════════════════════════════════════════

class ServicePackage(models.Model):
    SERVICE_TYPES = [
        ('consultation',   'Consultation'),
        ('document_prep',  'Document Preparation'),
        ('project',        'Project-Based'),
        ('retainer',       'Monthly Retainer'),
    ]

    department   = models.ForeignKey(Department, on_delete=models.CASCADE,
                       related_name='packages')
    name         = models.CharField(max_length=150)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description  = models.TextField()
    deliverables = models.TextField(blank=True,
                       help_text='Bullet list of what the client receives')
    duration     = models.CharField(max_length=80,
                       help_text='e.g. "30 minutes", "2–3 business days", "Project-based"')
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    currency     = models.CharField(max_length=3, default='CAD')
    is_active    = models.BooleanField(default=True)
    is_featured  = models.BooleanField(default=False)
    order        = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['department', 'order', 'price']

    def __str__(self):
        return f'{self.department} — {self.name} ({self.currency} {self.price})'

    def price_display(self):
        return f'{self.currency} {self.price:,.2f}'


# ════════════════════════════════════════════════════════════════════════
# SERVICE BOOKING
# ════════════════════════════════════════════════════════════════════════

class ServiceBooking(models.Model):
    CLIENT_TYPE = [
        ('individual', 'Individual'),
        ('business',   'Business'),
    ]
    PAYMENT_STATUS = [
        ('pending',  'Pending'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]
    STATUS = [
        ('new',         'New'),
        ('assigned',    'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]

    # Service
    package      = models.ForeignKey(ServicePackage, on_delete=models.PROTECT,
                       related_name='bookings')
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL,
                       null=True, blank=True, related_name='bookings',
                       help_text='Assigned by HQ after payment')

    # Client
    client_type  = models.CharField(max_length=12, choices=CLIENT_TYPE, default='individual')
    full_name    = models.CharField(max_length=150)
    email        = models.EmailField()
    phone        = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=200, blank=True)

    # Request
    problem_description = models.TextField(
        help_text='Client describes the problem or task they need help with')
    urgency  = models.CharField(max_length=20, choices=[
        ('standard', 'Standard'),
        ('urgent',   'Urgent — within 24 hrs'),
    ], default='standard')

    # Payment
    amount           = models.DecimalField(max_digits=10, decimal_places=2)
    currency         = models.CharField(max_length=3, default='CAD')
    payment_status   = models.CharField(max_length=12, choices=PAYMENT_STATUS, default='pending')
    moneris_order_id = models.CharField(max_length=100, blank=True)
    paid_at          = models.DateTimeField(null=True, blank=True)

    # Status
    status    = models.CharField(max_length=15, choices=STATUS, default='new')
    hq_notes  = models.TextField(blank=True, help_text='Internal notes — not visible to client')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Service Booking'
        verbose_name_plural = 'Service Bookings'

    def __str__(self):
        return f'{self.ref()} — {self.full_name} ({self.package})'

    def ref(self):
        return f'SB-{self.pk:04d}'
