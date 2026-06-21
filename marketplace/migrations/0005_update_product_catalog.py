from decimal import Decimal
from django.db import migrations

# ── Final 16-product catalog (replaces the old generic 18-item list) ──────────
# Each entry is matched/created by `name`. Stock photo URLs are Unsplash
# (free license, no attribution required) — same pattern already used on the
# homepage offer cards. They act as a fallback only: if a real photo is later
# uploaded via Django Admin, Product.safe_image_url automatically prefers it.

FINAL_PRODUCTS = [
    # ── Coffee ────────────────────────────────────────────────────────────────
    dict(name='Arabica Green Coffee', category='coffee', gender_target='all',
         description='High-altitude Arabica green coffee beans — smooth, nuanced flavour with bright acidity. Sourced from Uganda and Kenya.',
         price=Decimal('35.00'), currency='USD', quantity_available=400, unit='kg',
         market_type='both', origin_country='UG', is_featured=True,
         image_url='https://images.unsplash.com/photo-1561766858-62033ae40ec3?w=600&h=400&fit=crop&q=80'),

    dict(name='Robusta Green Coffee', category='coffee', gender_target='all',
         description='Premium Robusta green coffee beans sourced from Uganda. Rich, bold flavour profile ideal for espresso blends. Sold per kilogram.',
         price=Decimal('28.00'), currency='USD', quantity_available=500, unit='kg',
         market_type='both', origin_country='UG', is_featured=True,
         image_url='https://images.unsplash.com/photo-1703646619157-eb553d16d402?w=600&h=400&fit=crop&q=80'),

    # ── Suits — Men ───────────────────────────────────────────────────────────
    dict(name='Black Suit for Men', category='clothing', gender_target='men',
         description='Classic black two-piece business suit. Tailored fit, wrinkle-resistant fabric, fully lined jacket. Sizes S–3XL.',
         price=Decimal('180.00'), currency='USD', quantity_available=80, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1618886614638-80e3c103d31a?w=600&h=400&fit=crop&q=80'),

    dict(name='Navy Blue Suit for Men', category='clothing', gender_target='men',
         description='Sharp navy blue two-piece business suit. Tailored fit, wrinkle-resistant fabric, fully lined jacket. Sizes S–3XL.',
         price=Decimal('180.00'), currency='USD', quantity_available=70, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1617137968427-85924c800a22?w=600&h=400&fit=crop&q=80'),

    # ── Suits — Women ─────────────────────────────────────────────────────────
    dict(name='Black Suit for Women', category='clothing', gender_target='women',
         description='Elegant black tailored suit jacket and trousers. Office-ready cut with a modern silhouette. Sizes XS–2XL.',
         price=Decimal('185.00'), currency='USD', quantity_available=60, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1604904612715-47bf9d9bc670?w=600&h=400&fit=crop&q=80'),

    dict(name='Navy Blue Suit for Women', category='clothing', gender_target='women',
         description='Polished navy blue tailored suit jacket and trousers. Office-ready cut with a modern silhouette. Sizes XS–2XL.',
         price=Decimal('185.00'), currency='USD', quantity_available=55, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600&h=400&fit=crop&q=80'),

    # ── Shirts — Men ──────────────────────────────────────────────────────────
    dict(name='White Shirt for Men', category='clothing', gender_target='men',
         description='Crisp white formal cotton shirt. Button-down collar, machine washable. Sizes S–3XL.',
         price=Decimal('35.00'), currency='USD', quantity_available=200, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1611095790444-1dfa35e37b52?w=600&h=400&fit=crop&q=80'),

    dict(name='Blue Shirt for Men', category='clothing', gender_target='men',
         description='Light blue formal cotton shirt. Button-down collar, machine washable. Sizes S–3XL.',
         price=Decimal('35.00'), currency='USD', quantity_available=180, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1624835567150-0c530a20d8cc?w=600&h=400&fit=crop&q=80'),

    # ── T-Shirts ──────────────────────────────────────────────────────────────
    dict(name='Brown T-Shirt for Women', category='clothing', gender_target='women',
         description='Lightweight women\'s T-shirt in soft brown cotton. Relaxed fit, breathable fabric. Sizes XS–2XL.',
         price=Decimal('16.00'), currency='USD', quantity_available=220, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1586209418353-a2e51b9453d6?w=600&h=400&fit=crop&q=80'),

    dict(name='Grey T-Shirt for Men', category='clothing', gender_target='men',
         description='Comfortable 100% cotton T-shirt in heather grey. Lightweight and breathable. Sizes S–3XL.',
         price=Decimal('18.00'), currency='USD', quantity_available=250, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1618354691438-25bc04584c23?w=600&h=400&fit=crop&q=80'),

    # ── Shoes ─────────────────────────────────────────────────────────────────
    dict(name='Shoes for Men', category='shoes', gender_target='men',
         description='Classic leather dress shoes with rubber sole. Available in black and tan. Sizes 39–47.',
         price=Decimal('95.00'), currency='USD', quantity_available=100, unit='pair',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1592776063351-ce91e931457c?w=600&h=400&fit=crop&q=80'),

    dict(name='Shoes for Women', category='shoes', gender_target='women',
         description='Elegant pointed-toe pumps in premium faux leather. Available in black, nude and brown. Sizes 35–42.',
         price=Decimal('75.00'), currency='USD', quantity_available=90, unit='pair',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=600&h=400&fit=crop&q=80'),

    # ── Watches — Men ─────────────────────────────────────────────────────────
    dict(name='Silver Coated Hand Watch for Men', category='watches', gender_target='men',
         description='Classic silver-coated stainless steel quartz watch with date display. Water resistant to 30m.',
         price=Decimal('120.00'), currency='USD', quantity_available=70, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1613704193420-a53cab02d194?w=600&h=400&fit=crop&q=80'),

    dict(name='Gold Coated Hand Watch for Men', category='watches', gender_target='men',
         description='Elegant gold-coated stainless steel quartz watch with date display. Water resistant to 30m.',
         price=Decimal('135.00'), currency='USD', quantity_available=60, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1541778480-fc1752bbc2a9?w=600&h=400&fit=crop&q=80'),

    # ── Watches — Women ───────────────────────────────────────────────────────
    dict(name='Diamond Coated Hand Watch for Women', category='watches', gender_target='women',
         description='Luxury diamond-coated watch with a slim case and refined bracelet strap. Quartz movement, mineral crystal glass.',
         price=Decimal('210.00'), currency='USD', quantity_available=40, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1451477334999-a9321157a431?w=600&h=400&fit=crop&q=80'),

    dict(name='Gold Coated Hand Watch for Women', category='watches', gender_target='women',
         description='Slim women\'s watch with gold-coated case and bracelet strap. Quartz movement, mineral crystal glass.',
         price=Decimal('140.00'), currency='USD', quantity_available=55, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1604242692760-2f7b0c26856d?w=600&h=400&fit=crop&q=80'),
]

FINAL_NAMES = [p['name'] for p in FINAL_PRODUCTS]


def update_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')

    for data in FINAL_PRODUCTS:
        name = data['name']
        existing = Product.objects.filter(name=name).first()
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            existing.is_active = True
            existing.save()
        else:
            Product.objects.create(is_active=True, **data)

    # Deactivate every other product (old generic catalog) rather than
    # deleting — preserves any order history tied to them.
    Product.objects.exclude(name__in=FINAL_NAMES).update(is_active=False)


def reverse_update_products(apps, schema_editor):
    # Not meaningfully reversible (original state of consolidated/edited
    # products isn't recoverable) — no-op on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_product_image_url_product_video_alter_product_image_and_more'),
    ]

    operations = [
        migrations.RunPython(update_products, reverse_update_products),
    ]
