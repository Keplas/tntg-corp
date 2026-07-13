from django.db import migrations

def update_rates(apps, schema_editor):
    LoyaltySettings = apps.get_model("core", "LoyaltySettings")
    ls = LoyaltySettings.objects.first()
    if ls:
        ls.consumer_rate = 0.005   # 0.5%
        ls.referral_rate = 0.010   # 1.0%
        ls.save(update_fields=["consumer_rate", "referral_rate"])
    else:
        LoyaltySettings.objects.create(
            consumer_rate=0.005, referral_rate=0.010, payment_days=45
        )

class Migration(migrations.Migration):
    dependencies = [("core", "0003_add_blogpost")]
    operations   = [migrations.RunPython(update_rates, migrations.RunPython.noop)]
