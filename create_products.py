"""
Run after migrations to ensure merchandise products exist.
Called from build.sh: python create_products.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings')
django.setup()

from marketplace.models import Product
from accounts.models import CustomUser

seller = CustomUser.objects.filter(is_staff=True).first()

PRODUCTS = [
    {
        'name':               'T&TG Rustic Coffee Invitation Set',
        'category':           'coffee',
        'price':              '48.00',
        'currency':           'CAD',
        'unit':               'set',
        'quantity_available': 50,
        'market_type':        'both',
        'origin_country':     'Canada',
        'is_active':          True,
        'is_featured':        True,
        'description':        'Rustic coffee-themed invitation set. 10 cards on premium kraft paper with wax seal and dried flower accent. Perfect for T&TG trade events.',
    },
    {
        'name':               'T&TG Perfect Blend Gift Set',
        'category':           'coffee',
        'price':              '62.00',
        'currency':           'CAD',
        'unit':               'set',
        'quantity_available': 40,
        'market_type':        'both',
        'origin_country':     'Canada',
        'is_active':          True,
        'is_featured':        True,
        'description':        'Coffee-themed gift stationery — The Perfect Blend. 10 kraft paper cards with coffee cup tag and jute twine. Ideal for corporate gifting.',
    },
    {
        'name':               'T&TG Artisanal Luxury Coffee Pen',
        'category':           'coffee',
        'price':              '38.00',
        'currency':           'CAD',
        'unit':               'piece',
        'quantity_available': 100,
        'market_type':        'both',
        'origin_country':     'Canada',
        'is_active':          True,
        'is_featured':        False,
        'description':        'Premium handcrafted luxury ballpoint pen with black and gold coffee-pattern design. Elegant corporate gift for T&TG trade partners.',
    },
    {
        'name':               'T&TG Coffee Notebook and Pen Set',
        'category':           'coffee',
        'price':              '35.00',
        'currency':           'CAD',
        'unit':               'set',
        'quantity_available': 75,
        'market_type':        'both',
        'origin_country':     'Canada',
        'is_active':          True,
        'is_featured':        False,
        'description':        'Premium dark coffee-brown spiral notebook with matching pen. 200 pages A5 lay-flat binding. Ideal for trade meetings and onboarding sessions.',
    },
    {
        'name':               'T&TG Handcrafted Wooden Fountain Pen',
        'category':           'coffee',
        'price':              '55.00',
        'currency':           'CAD',
        'unit':               'piece',
        'quantity_available': 30,
        'market_type':        'both',
        'origin_country':     'Canada',
        'is_active':          True,
        'is_featured':        True,
        'description':        'Exquisite artisan fountain pen in dark rosewood with gold-plated nib. Distinguished gift for T&TG trade partners and directors.',
    },
]

created_count = 0
for data in PRODUCTS:
    try:
        obj, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=dict(seller=seller, **data)
        )
        status = 'Created' if created else 'Exists'
        if created:
            created_count += 1
        print(f'{status}: {obj.name}')
    except Exception as e:
        print(f'Skip {data["name"]}: {e}')

print(f'Done. {created_count} new products created.')
