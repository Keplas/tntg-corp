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
    ('children', 'Children'),
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
    image             = models.ImageField(upload_to='products/', blank=True, null=True)
    video_url         = models.URLField(blank=True)
    market_type       = models.CharField(max_length=20, choices=MARKET_CHOICES, default='both')
    seller            = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='products')
    origin_country    = models.CharField(max_length=2, blank=True)
    is_active         = models.BooleanField(default=True)
    is_featured       = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def safe_image_url(self):
        if not self.image:
            return None
        try:
            url = self.image.url
            if url.startswith('/media/') or url.startswith('media/'):
                import os
                from django.conf import settings
                local_path = os.path.join(settings.BASE_DIR, 'media', str(self.image))
                if not os.path.exists(local_path):
                    return None
            return url
        except Exception:
            return None

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
