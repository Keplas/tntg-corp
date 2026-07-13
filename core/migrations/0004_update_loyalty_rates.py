from django.db import migrations


def set_rates(apps, schema_editor):
    """Force loyalty rates to 0.5% consumer, 1.0% referral."""
    LoyaltySettings = apps.get_model("core", "LoyaltySettings")
    # Update ALL existing rows
    LoyaltySettings.objects.all().update(
        consumer_rate=0.0050,   # 0.5%
        referral_rate=0.0100,   # 1.0%
    )
    # Create one if none exist
    if not LoyaltySettings.objects.exists():
        LoyaltySettings.objects.create(
            consumer_rate=0.0050,
            referral_rate=0.0100,
            payment_days=45,
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0003_add_blogpost")]
    operations   = [migrations.RunPython(set_rates, migrations.RunPython.noop)]
