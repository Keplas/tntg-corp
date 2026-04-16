from django.db import models

class Notification(models.Model):
    NOTIF_TYPES = [
        ('order_placed', '🛒 New Order Placed'),
        ('order_updated', '📦 Order Status Updated'),
        ('registration', '👤 New User Registered'),
        ('partnership', '🤝 Partnership Request'),
        ('contact', '📩 New Contact Inquiry'),
        ('sell_order', '💰 Avon Points Sell Order'),
        ('insurance', '🛡️ Insurance Request'),
        ('brokerage', '📈 Brokerage Account Request'),
        ('training', '🎓 New Enrollment'),
        ('kyc', '🪪 KYC Submission'),
        ('general', '🔔 General'),
    ]
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
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
