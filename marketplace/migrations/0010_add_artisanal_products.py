from django.db import migrations

ARTISANAL_PRODUCTS = [
    dict(
        name='T&TG Instant Coffee — Medium Roast',
        category='coffee',
        gender_target='all',
        description=(
            'T&TG Instant Coffee Medium Roast — 100g glass jar. '
            'Smooth, Rich and Satisfying. 100% quality coffee with rich aroma and smooth taste. '
            'Pure coffee, no preservatives. Makes up to 55 cups per jar. '
            'Crafted and packaged in Canada. No artificial additives. '
            'Part of the T&TG Artisanal Coffee Based Goods range.'
        ),
        price=12.99,
        currency='USD',
        quantity_available=200,
        unit='jar (100g)',
        market_type='both',
        origin_country='CA',
        is_featured=True,
        image_url='/static/images/products/tntg_instant_coffee.jpg',
    ),
    dict(
        name='T&TG Coffee & Clove Soap — with Cinnamon Ground Coffee',
        category='coffee',
        gender_target='all',
        description=(
            'T&TG Soap — Coffee & Clove with Cinnamon Ground Coffee. '
            'All natural cold process soap, plant based, pure ingredients, planet friendly. '
            'Made with ground coffee beans, clove and cinnamon for a naturally exfoliating cleanse. '
            'No synthetic chemicals. Handcrafted in Canada under the T&TG Artisanal Coffee Based Goods label. '
            '"Naturally Clean, Naturally You."'
        ),
        price=8.99,
        currency='USD',
        quantity_available=150,
        unit='bar',
        market_type='both',
        origin_country='CA',
        is_featured=True,
        image_url='/static/images/products/tntg_coffee_clove_soap.jpg',
    ),
    dict(
        name='Belfour Coffee Bar Soap — 150g',
        category='coffee',
        gender_target='all',
        description=(
            'Belfour Coffee Bar Soap — 150 grams. Whitening, Exfoliating, Anti-Aging and Anti-Cellulite. '
            'Enriched with Vitamin B3 (Niacinamide) for skin brightening. '
            'Infused with real coffee bean extracts for deep exfoliation and antioxidant benefits. '
            'Canada made. Available through T&TG Trade Corp as part of our Artisanal Coffee Based Goods range.'
        ),
        price=7.99,
        currency='USD',
        quantity_available=180,
        unit='bar (150g)',
        market_type='both',
        origin_country='CA',
        is_featured=False,
        image_url='/static/images/products/belfour_coffee_soap.jpg',
    ),
    dict(
        name='T&TG Artisanal Coffee Swirl Soap — Handcrafted',
        category='coffee',
        gender_target='all',
        description=(
            'T&TG Artisanal Coffee Swirl Soap — handcrafted in Canada. '
            'Made with premium whole coffee beans and rich coffee-infused oils swirled into a beautiful marbled pattern. '
            'Natural exfoliant for smooth, refreshed skin. No synthetic fragrances or preservatives. '
            'Each bar is individually crafted — part of the T&TG Artisanal Coffee Based Goods range. '
            'Canada made with love.'
        ),
        price=9.99,
        currency='USD',
        quantity_available=120,
        unit='bar',
        market_type='both',
        origin_country='CA',
        is_featured=True,
        image_url='/static/images/products/tntg_artisanal_swirl_soap.jpg',
    ),
]


def add_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    for data in ARTISANAL_PRODUCTS:
        existing = Product.objects.filter(name=data['name']).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            existing.is_active = True
            existing.save()
        else:
            Product.objects.create(is_active=True, **data)


def reverse_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    for data in ARTISANAL_PRODUCTS:
        Product.objects.filter(name=data['name']).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_add_wishlist'),
    ]

    operations = [
        migrations.RunPython(add_products, reverse_products),
    ]
