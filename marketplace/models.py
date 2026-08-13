from cloudinary.models import CloudinaryField
from django.db import models
from accounts.models import CustomUser

CATEGORY_CHOICES = [
    ('clothing', 'Clothing'),
    ('shoes',    'Shoes'),
    ('watches',  'Watches'),
    ('coffee',   'Coffee'),
]

GENDER_TARGET_CHOICES = [
    ('all',      'All'),
    ('men',      'Men'),
    ('women',    'Women'),
]


class Product(models.Model):
    MARKET_CHOICES = [('local','Local'),('international','International'),('both','Both')]

    name              = models.CharField(max_length=200)
    category          = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    gender_target     = models.CharField(max_length=10, choices=GENDER_TARGET_CHOICES, default='all',
                                         verbose_name='Target Audience')
    description       = models.TextField()
    price             = models.DecimalField(max_digits=12, decimal_places=2)
    currency          = models.CharField(max_length=5, default='USD')
    quantity_available= models.IntegerField(default=0)
    unit              = models.CharField(max_length=50, default='unit')
    image             = CloudinaryField('image', folder='tntg/products', blank=True, null=True,
                                          help_text='Upload photo — stored on Cloudinary CDN.')
    image_url         = models.URLField(blank=True,
                                        help_text='Stock/placeholder photo link — used only if no photo is uploaded above.')
    video             = models.FileField(upload_to='products/videos/', blank=True, null=True,
                                         help_text='Upload your own product video — takes priority over Video URL below.')
    video_url         = models.URLField(blank=True,
                                        help_text='YouTube/Vimeo link — used only if no video is uploaded above.')
    market_type       = models.CharField(max_length=20, choices=MARKET_CHOICES, default='both')
    seller            = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='products')
    origin_country    = models.CharField(max_length=2, blank=True)
    is_active         = models.BooleanField(default=True)
    is_featured       = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


    def get_country_prices(self):
        """
        Returns list of {country, flag, currency, symbol, price, is_override}
        Priority: manual override > live forex > static fallback rates.
        Never raises — always returns a list.
        """
        from decimal import Decimal

        COUNTRIES = [
            ('Canada',      'CAD', 'CA$', '🇨🇦'),
            ('USA',         'USD', 'US$', '🇺🇸'),
            ('Uganda',      'UGX', 'UGX',  '🇺🇬'),
            ('Kenya',       'KES', 'KES',  '🇰🇪'),
            ('Netherlands', 'EUR', '€',    '🇳🇱'),
            ('Japan',       'JPY', '¥',    '🇯🇵'),
        ]

        # Static fallback rates (USD base) — updated when API unavailable
        STATIC_RATES = {
            'CAD': 1.36, 'USD': 1.0, 'UGX': 3750.0,
            'KES': 129.0, 'EUR': 0.92, 'JPY': 157.0,
        }

        try:
            from core.exchange_rates import fetch_live_rates
            rates = fetch_live_rates() or STATIC_RATES
        except Exception:
            rates = STATIC_RATES

        base   = Decimal(str(self.price))
        base_c = self.currency or 'CAD'

        def to_usd(amount, currency):
            r = Decimal(str(rates.get(currency, 1) or 1))
            return amount / r

        def from_usd(amount, currency):
            r = Decimal(str(rates.get(currency, 1) or 1))
            return amount * r

        base_usd = to_usd(base, base_c)

        # Safe override lookup
        try:
            overrides = {op.country: op for op in self.country_prices.filter(is_active=True)}
        except Exception:
            overrides = {}

        result = []
        for country, currency, symbol, flag in COUNTRIES:
            if country in overrides:
                op = overrides[country]
                result.append({
                    'country':     country,
                    'flag':        flag,
                    'currency':    op.currency,
                    'symbol':      symbol,
                    'price':       op.price,
                    'is_override': True,
                })
            else:
                try:
                    converted = from_usd(base_usd, currency)
                    if currency in ('UGX', 'KES', 'JPY'):
                        converted = converted.quantize(Decimal('1'))
                    else:
                        converted = converted.quantize(Decimal('0.01'))
                    result.append({
                        'country':     country,
                        'flag':        flag,
                        'currency':    currency,
                        'symbol':      symbol,
                        'price':       converted,
                        'is_override': False,
                    })
                except Exception:
                    pass
        return result

    @property
    def safe_image_url(self):
        """
        Priority order:
        1. CloudinaryField (self.image) — build full URL from public_id
        2. External URL (self.image_url) — direct URL field
        """
        import os
        from django.conf import settings as djsettings

        # ── Try CloudinaryField first ─────────────────────────────────────
        if self.image:
            raw = str(self.image)  # stores public_id e.g. "tntg/products/abc123"
            # If it already looks like a full URL, return it
            if raw.startswith('http'):
                return raw
            # Build Cloudinary URL from public_id + env config
            cloud = getattr(djsettings, 'CLOUDINARY_CLOUD_NAME', '')
            if cloud and raw:
                return f'https://res.cloudinary.com/{cloud}/image/upload/{raw}'
            # Try .url attribute as last resort
            try:
                url = self.image.url
                if url and url.startswith('http'):
                    return url
            except Exception:
                pass

        # ── Fall back to image_url field ──────────────────────────────────
        if self.image_url:
            return self.image_url

        return None

    @property
    def safe_video_url(self):
        if self.video:
            try:
                url = self.video.url
                if url.startswith('/media/') or url.startswith('media/'):
                    import os
                    from django.conf import settings
                    local_path = os.path.join(settings.BASE_DIR, 'media', str(self.video))
                    if not os.path.exists(local_path):
                        return self.video_url or None
                return url
            except Exception:
                return self.video_url or None
        return self.video_url or None

    def loyalty_points_consumer(self):
        """1% of price for the end-user/consumer (rate comes from LoyaltySettings)."""
        from core.models import LoyaltySettings
        rate = float(LoyaltySettings.get_settings().consumer_rate)
        return round(float(self.price) * rate, 2)

    def loyalty_points_referral(self):
        """2.5% of price for the referrer (rate comes from LoyaltySettings)."""
        from core.models import LoyaltySettings
        rate = float(LoyaltySettings.get_settings().referral_rate)
        return round(float(self.price) * rate, 2)

    # Legacy aliases so old templates don't break
    def avon_points_consumer(self):
        return self.loyalty_points_consumer()

    def avon_points_referral(self):
        return self.loyalty_points_referral()


class Order(models.Model):
    ORDER_TYPE    = [('buy','Buy'),('sell','Sell')]
    DELIVERY_TYPE = [('express','Express'),('ordinary','Ordinary')]
    STATUS_CHOICES= [
        ('pending','Pending'),('processing','Processing'),
        ('accepted','Accepted'),('not_accepted','Not Accepted'),
        ('shipped','Shipped'),('delivered','Delivered'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('unpaid',   'Unpaid'),
        ('pending',  'Payment Pending'),
        ('paid',     'Paid'),
        ('failed',   'Payment Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('card',         'Card (Stripe)'),
        ('mobile_money', 'Mobile Money (Flutterwave)'),
    ]

    buyer               = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type          = models.CharField(max_length=10, choices=ORDER_TYPE, default='buy')
    quantity            = models.IntegerField(default=1)
    total_price         = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_type       = models.CharField(max_length=10, choices=DELIVERY_TYPE, default='ordinary')
    destination_country = models.CharField(max_length=100)
    destination_address = models.TextField()
    desired_arrival_date= models.DateField()
    desired_arrival_time= models.TimeField(blank=True, null=True)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    referred_by         = models.CharField(max_length=200, blank=True)
    referrer_unique_id  = models.CharField(max_length=50, blank=True)
    avon_points_earned  = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              verbose_name='Loyalty Points Earned')
    reward_payment_date = models.DateField(blank=True, null=True,
                                           verbose_name='Reward Payment Due Date',
                                           help_text='Automatically set to 45 days after purchase')
    # Payment tracking
    payment_status    = models.CharField(max_length=12, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method    = models.CharField(max_length=14, choices=PAYMENT_METHOD_CHOICES, blank=True)
    display_currency   = models.CharField(max_length=3, default="CAD", blank=True, help_text="Currency chosen by buyer at checkout")
    display_total     = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, help_text="Total in buyer's chosen currency")
    exchange_rate_used= models.DecimalField(max_digits=14, decimal_places=6, null=True, blank=True, help_text="Rate at time of checkout")
    payment_reference = models.CharField(max_length=120, blank=True,
                                          help_text='Stripe session ID or Flutterwave transaction ref')
    paid_at           = models.DateTimeField(blank=True, null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.buyer.username} — {self.product.name}"


class ProductReview(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating     = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.product.name} ({self.rating}★)"


class Wishlist(models.Model):
    user    = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added   = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user','product')
    def __str__(self):
        return f"{self.user.username} ♥ {self.product.name}"


class BulkOrder(models.Model):
    """Wholesale / bulk order for B2B clients."""
    STATUS = [
        ('pending','Pending Review'),('quoted','Quote Sent'),
        ('confirmed','Confirmed'),('rejected','Rejected'),('fulfilled','Fulfilled'),
    ]
    buyer            = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='bulk_orders')
    company_name     = models.CharField(max_length=200, blank=True)
    destination      = models.CharField(max_length=100)
    product_type     = models.CharField(max_length=100)
    quantity_kg      = models.DecimalField(max_digits=10, decimal_places=2)
    frequency        = models.CharField(max_length=50, blank=True)
    notes            = models.TextField(blank=True)
    quoted_price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"Bulk #{self.pk} — {self.buyer.username} — {self.quantity_kg}kg"


class ProductCountryPrice(models.Model):
    """Optional manual price override per product per country."""
    COUNTRIES = [
        ('Canada',              'Canada (CAD)'),
        ('USA',                 'USA (USD)'),
        ('Uganda',              'Uganda (UGX)'),
        ('Kenya',               'Kenya (KES)'),
        ('Netherlands',         'Netherlands (EUR)'),
        ('Japan',               'Japan (JPY)'),
    ]
    CURRENCIES = [
        ('CAD','CAD'),('USD','USD'),('UGX','UGX'),
        ('KES','KES'),('EUR','EUR'),('JPY','JPY'),
    ]
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='country_prices')
    country    = models.CharField(max_length=20, choices=COUNTRIES)
    price      = models.DecimalField(max_digits=12, decimal_places=2)
    currency   = models.CharField(max_length=3, choices=CURRENCIES)
    is_active  = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'country']
        ordering = ['country']

    def __str__(self):
        return f"{self.product.name} — {self.country}: {self.currency} {self.price}"
