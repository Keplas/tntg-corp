from django.db import migrations


def add_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    User    = apps.get_model('accounts', 'CustomUser')
    seller  = User.objects.filter(is_staff=True).first()

    products = [
        {
            'name':               'T&TG Rustic Coffee Invitation Set',
            'category':           'coffee',
            'description':        'Rustic coffee-themed invitation set. 10 invitations on kraft paper with wax seal, twine and dried flower accent. For T&TG trade events and coffee ceremonies.',
            'price':              '48.00',
            'currency':           'CAD',
            'unit':               'set',
            'quantity_available': 50,
            'market_type':        'both',
            'origin_country':     'Canada',
            'is_active':          True,
            'is_featured':        True,
        },
        {
            'name':               "T&TG 'The Perfect Blend' Gift Set",
            'category':           'coffee',
            'description':        "Coffee-themed gift stationery set — 'The Perfect Blend'. 10 kraft paper cards with coffee cup tag and jute twine. Ideal for corporate gifting and trade partner welcome packs.",
            'price':              '62.00',
            'currency':           'CAD',
            'unit':               'set',
            'quantity_available': 40,
            'market_type':        'both',
            'origin_country':     'Canada',
            'is_active':          True,
            'is_featured':        True,
        },
        {
            'name':               'T&TG Artisanal Luxury Coffee Pen',
            'category':           'coffee',
            'description':        'Premium handcrafted luxury ballpoint pen with black and gold coffee-pattern design. Smooth German ink refill. Elegant corporate gift for T&TG trade partners.',
            'price':              '38.00',
            'currency':           'CAD',
            'unit':               'piece',
            'quantity_available': 100,
            'market_type':        'both',
            'origin_country':     'Canada',
            'is_active':          True,
            'is_featured':        False,
        },
        {
            'name':               'T&TG Coffee Notebook & Pen Set',
            'category':           'coffee',
            'description':        'Premium dark coffee-brown spiral notebook with matching pen. 200 pages, A5 size, lay-flat binding. Ideal for trade meetings and onboarding sessions.',
            'price':              '35.00',
            'currency':           'CAD',
            'unit':               'set',
            'quantity_available': 75,
            'market_type':        'both',
            'origin_country':     'Canada',
            'is_active':          True,
            'is_featured':        False,
        },
        {
            'name':               'T&TG Handcrafted Wooden Fountain Pen',
            'category':           'coffee',
            'description':        'Exquisite artisan fountain pen in dark rosewood and olive wood with gold-plated nib. Each pen is unique. Distinguished gift for T&TG trade partners and directors.',
            'price':              '55.00',
            'currency':           'CAD',
            'unit':               'piece',
            'quantity_available': 30,
            'market_type':        'both',
            'origin_country':     'Canada',
            'is_active':          True,
            'is_featured':        True,
        },
    ]

    for data in products:
        try:
            if not Product.objects.filter(name=data['name']).exists():
                Product.objects.create(seller=seller, **data)
        except Exception:
            pass  # Skip if any field issue — Tom can add via admin


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0015_add_display_currency_to_order'),
    ]

    operations = [
        migrations.RunPython(add_products, migrations.RunPython.noop),
    ]
