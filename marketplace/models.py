from django.db import models
from accounts.models import CustomUser

CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('coffee', 'Coffee'),
    ('pharmaceuticals', 'Pharmaceuticals'),
    ('agriculture', 'Agriculture'),
    ('textiles', 'Textiles'),
    ('machinery', 'Machinery'),
    ('other', 'Other'),
]

class Product(models.Model):
    MARKET_CHOICES = [('local','Local'),('international','International'),('both','Both')]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    quantity_available = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default='unit')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    market_type = models.CharField(max_length=20, choices=MARKET_CHOICES, default='both')
    seller = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    origin_country = models.CharField(max_length=2, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def avon_points_consumer(self):
        return round(float(self.price) / 5.5, 2)

    def avon_points_referral(self):
        return round(float(self.price) / 8.5, 2)

class Order(models.Model):
    ORDER_TYPE = [('buy','Buy'),('sell','Sell')]
    DELIVERY_TYPE = [('express','Express'),('ordinary','Ordinary')]
    STATUS_CHOICES = [('pending','Pending'),('processing','Processing'),('accepted','Accepted'),('not_accepted','Not Accepted'),('shipped','Shipped'),('delivered','Delivered')]

    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE, default='buy')
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE, default='ordinary')
    destination_country = models.CharField(max_length=100)
    destination_address = models.TextField()
    desired_arrival_date = models.DateField()
    desired_arrival_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    referred_by = models.CharField(max_length=200, blank=True)
    referrer_unique_id = models.CharField(max_length=50, blank=True)
    avon_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.buyer.username} - {self.product.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"
