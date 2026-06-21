from django.db import migrations

# Mid-market rates as of June 2026 — source: Xe.com / Wise.com.
# These are a starting point, not a live feed. Update periodically via
# Django admin (Services > Forex rates) to keep mobile money charges
# accurate — a stale rate means customers get charged the wrong amount.
USD_RATES = [
    ('USD', 'UGX', 3641.00),
    ('USD', 'KES', 129.40),
    ('UGX', 'USD', 0.0002747),
    ('KES', 'USD', 0.0077280),
]


def add_usd_rates(apps, schema_editor):
    ForexRate = apps.get_model('services', 'ForexRate')
    for from_c, to_c, rate in USD_RATES:
        ForexRate.objects.get_or_create(
            from_currency=from_c, to_currency=to_c, defaults={'rate': rate}
        )


def remove_usd_rates(apps, schema_editor):
    ForexRate = apps.get_model('services', 'ForexRate')
    for from_c, to_c, _ in USD_RATES:
        ForexRate.objects.filter(from_currency=from_c, to_currency=to_c).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_usd_rates, remove_usd_rates),
    ]
