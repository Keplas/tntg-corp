from django.contrib.auth.models import AbstractUser
from django.db import models

COUNTRY_CHOICES = [
    ('CA', 'Canada 🇨🇦'),
    ('UG', 'Uganda 🇺🇬'),
    ('KE', 'Kenya 🇰🇪'),
]

MARKET_TYPE_CHOICES = [
    ('local',         'Local Market'),
    ('international', 'International Market'),
    ('both',          'Both'),
]

USER_ROLE_CHOICES = [
    ('buyer',  'Buyer'),
    ('seller', 'Seller'),
    ('partner','Partner Company'),
    ('both',   'Buyer & Seller'),
]

TERM_CHOICES = [
    ('short', 'Short Term'),
    ('long',  'Long Term'),
]


class CustomUser(AbstractUser):
    unique_id             = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone                 = models.CharField(max_length=20, blank=True)
    country               = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    city                  = models.CharField(max_length=100, blank=True)
    address               = models.TextField(blank=True)
    profile_photo         = models.ImageField(upload_to='profiles/', blank=True, null=True)
    national_id_front     = models.ImageField(upload_to='kyc/', blank=True, null=True)
    national_id_back      = models.ImageField(upload_to='kyc/', blank=True, null=True)
    selfie                = models.ImageField(upload_to='kyc/', blank=True, null=True)
    market_type           = models.CharField(max_length=20, choices=MARKET_TYPE_CHOICES, default='local')
    user_role             = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='buyer')
    term_preference       = models.CharField(max_length=10, choices=TERM_CHOICES, default='short')
    business_description  = models.TextField(blank=True)
    declaration           = models.FileField(upload_to='declarations/', blank=True, null=True)
    is_partner            = models.BooleanField(default=False)
    is_verified           = models.BooleanField(default=False)
    partner_company       = models.CharField(max_length=200, blank=True)
    partner_id            = models.CharField(max_length=50, blank=True)
    has_certificate       = models.BooleanField(default=False)
    is_registered_company = models.BooleanField(default=False)
    avon_points           = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='T&TG Loyalty Points'
    )
    joined_date    = models.DateTimeField(auto_now_add=True)
    bio            = models.TextField(blank=True)
    profile_link   = models.CharField(max_length=100, blank=True, unique=True, null=True)
    website        = models.URLField(blank=True)


    # ── Security fields ───────────────────────────────────────────────────────
    login_attempts         = models.PositiveSmallIntegerField(default=0)
    locked_until           = models.DateTimeField(null=True, blank=True)
    email_verified         = models.BooleanField(default=False)
    email_verify_token     = models.CharField(max_length=64, blank=True)
    password_reset_token   = models.CharField(max_length=64, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    withdrawal_pin         = models.CharField(max_length=128, blank=True)
    withdrawal_pin_set     = models.BooleanField(default=False)
    daily_withdrawal_limit = models.DecimalField(max_digits=10, decimal_places=2, default=500)

    @property
    def safe_profile_photo_url(self):
        if not self.profile_photo:
            return None
        try:
            url = self.profile_photo.url
            if url.startswith('http'):
                return url
            import os
            from django.conf import settings as djsettings
            local_path = os.path.join(djsettings.MEDIA_ROOT, str(self.profile_photo))
            if os.path.exists(local_path):
                return url
            return None
        except Exception:
            return None

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.unique_id or 'No ID'})"

    def save(self, *args, **kwargs):
        if not self.unique_id and self.pk:
            self.unique_id = f"TG{str(self.pk).zfill(5)}"
        super().save(*args, **kwargs)
        if not self.unique_id:
            self.unique_id = f"TG{str(self.pk).zfill(5)}"
            CustomUser.objects.filter(pk=self.pk).update(unique_id=self.unique_id)


class AvonPointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earn_purchase', 'Earned — Purchase'),
        ('earn_referral', 'Earned — Referral'),
        ('withdrawal',    'Withdrawal'),
        ('transfer',      'Transfer'),
    ]
    QUARTER_CHOICES = [('Q1','Q1'),('Q2','Q2'),('Q3','Q3'),('Q4','Q4')]
    STATUS_CHOICES  = [
        ('pending',      'Pending'),
        ('processing',   'Processing'),
        ('completed',    'Completed'),
        ('not_accepted', 'Not Accepted'),
    ]

    user             = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    points           = models.DecimalField(max_digits=12, decimal_places=2)
    quarter          = models.CharField(max_length=2, choices=QUARTER_CHOICES, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description      = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    min_execution_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name        = 'Loyalty Point Transaction'
        verbose_name_plural = 'Loyalty Point Transactions'

    def __str__(self):
        return f"{self.user.username} — {self.transaction_type} — {self.points} pts"
