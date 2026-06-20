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
        max_digits=6, decimal_places=4, default=0.0100,
        verbose_name='Consumer Reward Rate',
        help_text='End-user/consumer reward as a decimal — e.g. 0.0100 = 1%'
    )
    referral_rate = models.DecimalField(
        max_digits=6, decimal_places=4, default=0.0250,
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
