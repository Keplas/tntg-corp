from django.db import models


class Notification(models.Model):
    NOTIF_TYPES = [
        ('order_placed',  '🛒 New Order Placed'),
        ('order_updated', '📦 Order Status Updated'),
        ('registration',  '👤 New User Registered'),
        ('partnership',   '🤝 Partnership Request'),
        ('contact',       '📩 New Contact Inquiry'),
        ('sell_order',    '💰 Loyalty Points Withdrawal'),
        ('training',      '🎓 New Enrollment'),
        ('kyc',           '🪪 KYC Submission'),
        ('general',       '🔔 General'),
    ]
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='general')
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    link       = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{'READ' if self.is_read else 'UNREAD'}] {self.title}"

    @staticmethod
    def notify(notif_type, title, message, link=''):
        Notification.objects.create(
            notif_type=notif_type, title=title, message=message, link=link
        )


class LoyaltySettings(models.Model):
    """Admin-configurable rates and rules for the T&TG Trade Loyalty Platform."""
    consumer_rate = models.DecimalField(
        max_digits=6, decimal_places=4, default=0.0050,
        verbose_name='Consumer Reward Rate',
        help_text='End-user/consumer reward as a decimal — e.g. 0.0100 = 1%'
    )
    referral_rate = models.DecimalField(
        max_digits=6, decimal_places=4, default=0.0100,
        verbose_name='Referral Reward Rate',
        help_text='Reward for referring a buyer as a decimal — e.g. 0.0250 = 2.5%'
    )
    payment_days = models.IntegerField(
        default=45,
        verbose_name='Payment Processing Day',
        help_text='Number of days after purchase before the loyalty reward is processed'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Loyalty Settings'
        verbose_name_plural = 'Loyalty Settings'

    def __str__(self):
        return (
            f'Consumer: {float(self.consumer_rate)*100:.2f}% | '
            f'Referral: {float(self.referral_rate)*100:.2f}% | '
            f'Payment Day: {self.payment_days}'
        )

    @classmethod
    def get_settings(cls):
        """Returns the singleton settings row, creating defaults on first call."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('trade_news',    '📰 Trade News'),
        ('coffee_market', '☕ Coffee Market'),
        ('import_tips',   '🚢 Import & Export Tips'),
        ('east_africa',   '🌍 East Africa'),
        ('regulations',   '⚖️ Regulations & Compliance'),
        ('company_news',  '🏢 Company News'),
    ]

    title           = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True, max_length=220)
    excerpt         = models.TextField(max_length=400, help_text='Short summary shown on the blog listing page.')
    content         = models.TextField(help_text='Full article content. HTML is supported.')
    category        = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='trade_news')
    author          = models.ForeignKey(
                          'accounts.CustomUser', on_delete=models.SET_NULL,
                          null=True, blank=True, related_name='blog_posts'
                      )
    cover_image     = models.ImageField(upload_to='blog/', blank=True, null=True)
    cover_image_url = models.URLField(blank=True, help_text='Stock photo URL used if no image is uploaded.')
    is_published    = models.BooleanField(default=False)
    is_featured     = models.BooleanField(default=False, help_text='Show in the featured slot at the top of the blog.')
    views_count     = models.PositiveIntegerField(default=0)
    published_at    = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name        = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimated reading time in minutes (avg 200 words/min)."""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    @property
    def safe_cover_url(self):
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                pass
        return self.cover_image_url or ''
