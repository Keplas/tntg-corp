from django.db import migrations

TNTG_COFFEE_BAG = 'https://tntgcorp.com/static/images/products/tg-coffee-bag.jpg'

COFFEE_PRODUCTS = [
    dict(
        name='T&TG Arabica Green Coffee',
        category='coffee',
        gender_target='all',
        description=(
            'Premium high-altitude Arabica green coffee beans, sourced directly from Uganda\'s '
            'Kampala highlands and supplied exclusively under the T&TG Coffee label. '
            'Smooth, nuanced flavour with bright acidity. Sold per kilogram. '
            'Certified origin, traceable farm-to-port supply chain.'
        ),
        price=35.00,
        currency='USD',
        quantity_available=500,
        unit='kg',
        market_type='both',
        origin_country='UG',
        is_featured=True,
        image_url=TNTG_COFFEE_BAG,
    ),
    dict(
        name='T&TG Robusta Green Coffee',
        category='coffee',
        gender_target='all',
        description=(
            'Premium Robusta green coffee beans sourced from Uganda, supplied under the '
            'T&TG Coffee label. Rich, bold flavour profile — ideal for espresso blends '
            'and commercial roasters. Sold per kilogram. '
            'Certified origin, traceable farm-to-port supply chain.'
        ),
        price=28.00,
        currency='USD',
        quantity_available=600,
        unit='kg',
        market_type='both',
        origin_country='UG',
        is_featured=True,
        image_url=TNTG_COFFEE_BAG,
    ),
]

KEEP_NAMES = [p['name'] for p in COFFEE_PRODUCTS]


def coffee_only(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')

    # Deactivate every non-coffee product (keep for order history)
    Product.objects.exclude(category='coffee').update(is_active=False, is_featured=False)

    # Also deactivate old coffee entries without the T&TG label
    Product.objects.filter(category='coffee').exclude(name__in=KEEP_NAMES).update(is_active=False, is_featured=False)

    # Upsert the two T&TG-branded coffee products
    for data in COFFEE_PRODUCTS:
        existing = Product.objects.filter(name=data['name']).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            existing.is_active = True
            existing.save()
        else:
            Product.objects.create(is_active=True, **data)


def reverse_coffee_only(apps, schema_editor):
    pass  # Not meaningfully reversible


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0007_brand_coffee_products'),
    ]

    operations = [
        migrations.RunPython(coffee_only, reverse_coffee_only),
    ]
