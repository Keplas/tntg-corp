from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    """
    Sends a shipping-update email whenever an Order's status changes
    (e.g. admin marks it 'shipped' or 'delivered'). Compares against the
    previously-saved value in the database to detect an actual change —
    skips silently on order creation or unrelated field edits.
    """
    if not instance.pk:
        return  # new order — handled separately by send_order_placed_email
    try:
        previous = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return
    if previous.status != instance.status and instance.status in ('processing', 'accepted', 'shipped', 'delivered'):
        from core.emails import send_shipping_update_email
        send_shipping_update_email(instance)
