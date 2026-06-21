"""
seed_data.py — Run once to populate the database with initial data.
Usage:  python manage.py shell < seed_data.py
        OR:  exec(open('seed_data.py').read())  inside manage.py shell
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings')
django.setup()

from marketplace.models import Product
from services.models import ForexRate
from training.models import TrainingProgram, TVProgram
from core.models import LoyaltySettings

# ── 1. Loyalty Settings ──────────────────────────────────────────────────────
ls, created = LoyaltySettings.objects.get_or_create(pk=1)
ls.consumer_rate = 0.0100   # 1 %
ls.referral_rate = 0.0250   # 2.5 %
ls.payment_days  = 45
ls.save()
print(f"{'Created' if created else 'Updated'} LoyaltySettings → consumer 1%, referral 2.5%, payment Day 45")

# ── 2. Products ───────────────────────────────────────────────────────────────
PRODUCTS = [
    # ── Coffee ────────────────────────────────────────────────────────────────
    dict(name='Arabica Green Coffee', category='coffee', gender_target='all',
         description='High-altitude Arabica green coffee beans — smooth, nuanced flavour with bright acidity. Sourced from Uganda and Kenya.',
         price=35.00, currency='USD', quantity_available=400, unit='kg',
         market_type='both', origin_country='UG', is_featured=True,
         image_url='https://tntgcorp.com/static/images/products/tg-coffee-bag.jpg'),

    dict(name='Robusta Green Coffee', category='coffee', gender_target='all',
         description='Premium Robusta green coffee beans sourced from Uganda. Rich, bold flavour profile ideal for espresso blends. Sold per kilogram.',
         price=28.00, currency='USD', quantity_available=500, unit='kg',
         market_type='both', origin_country='UG', is_featured=True,
         image_url='https://tntgcorp.com/static/images/products/tg-coffee-bag.jpg'),

    # ── Suits — Men ───────────────────────────────────────────────────────────
    dict(name='Black Suit for Men', category='clothing', gender_target='men',
         description='Classic black two-piece business suit. Tailored fit, wrinkle-resistant fabric, fully lined jacket. Sizes S–3XL.',
         price=180.00, currency='USD', quantity_available=80, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1618886614638-80e3c103d31a?w=600&h=400&fit=crop&q=80'),

    dict(name='Navy Blue Suit for Men', category='clothing', gender_target='men',
         description='Sharp navy blue two-piece business suit. Tailored fit, wrinkle-resistant fabric, fully lined jacket. Sizes S–3XL.',
         price=180.00, currency='USD', quantity_available=70, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1617137968427-85924c800a22?w=600&h=400&fit=crop&q=80'),

    # ── Suits — Women ─────────────────────────────────────────────────────────
    dict(name='Black Suit for Women', category='clothing', gender_target='women',
         description='Elegant black tailored suit jacket and trousers. Office-ready cut with a modern silhouette. Sizes XS–2XL.',
         price=185.00, currency='USD', quantity_available=60, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1604904612715-47bf9d9bc670?w=600&h=400&fit=crop&q=80'),

    dict(name='Navy Blue Suit for Women', category='clothing', gender_target='women',
         description='Polished navy blue tailored suit jacket and trousers. Office-ready cut with a modern silhouette. Sizes XS–2XL.',
         price=185.00, currency='USD', quantity_available=55, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600&h=400&fit=crop&q=80'),

    # ── Shirts — Men ──────────────────────────────────────────────────────────
    dict(name='White Shirt for Men', category='clothing', gender_target='men',
         description='Crisp white formal cotton shirt. Button-down collar, machine washable. Sizes S–3XL.',
         price=35.00, currency='USD', quantity_available=200, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1611095790444-1dfa35e37b52?w=600&h=400&fit=crop&q=80'),

    dict(name='Blue Shirt for Men', category='clothing', gender_target='men',
         description='Light blue formal cotton shirt. Button-down collar, machine washable. Sizes S–3XL.',
         price=35.00, currency='USD', quantity_available=180, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1624835567150-0c530a20d8cc?w=600&h=400&fit=crop&q=80'),

    # ── T-Shirts ──────────────────────────────────────────────────────────────
    dict(name='Brown T-Shirt for Women', category='clothing', gender_target='women',
         description='Lightweight women\'s T-shirt in soft brown cotton. Relaxed fit, breathable fabric. Sizes XS–2XL.',
         price=16.00, currency='USD', quantity_available=220, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1586209418353-a2e51b9453d6?w=600&h=400&fit=crop&q=80'),

    dict(name='Grey T-Shirt for Men', category='clothing', gender_target='men',
         description='Comfortable 100% cotton T-shirt in heather grey. Lightweight and breathable. Sizes S–3XL.',
         price=18.00, currency='USD', quantity_available=250, unit='piece',
         market_type='local', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1618354691438-25bc04584c23?w=600&h=400&fit=crop&q=80'),

    # ── Shoes ─────────────────────────────────────────────────────────────────
    dict(name='Shoes for Men', category='shoes', gender_target='men',
         description='Classic leather dress shoes with rubber sole. Available in black and tan. Sizes 39–47.',
         price=95.00, currency='USD', quantity_available=100, unit='pair',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1592776063351-ce91e931457c?w=600&h=400&fit=crop&q=80'),

    dict(name='Shoes for Women', category='shoes', gender_target='women',
         description='Elegant pointed-toe pumps in premium faux leather. Available in black, nude and brown. Sizes 35–42.',
         price=75.00, currency='USD', quantity_available=90, unit='pair',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=600&h=400&fit=crop&q=80'),

    # ── Watches — Men ─────────────────────────────────────────────────────────
    dict(name='Silver Coated Hand Watch for Men', category='watches', gender_target='men',
         description='Classic silver-coated stainless steel quartz watch with date display. Water resistant to 30m.',
         price=120.00, currency='USD', quantity_available=70, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1613704193420-a53cab02d194?w=600&h=400&fit=crop&q=80'),

    dict(name='Gold Coated Hand Watch for Men', category='watches', gender_target='men',
         description='Elegant gold-coated stainless steel quartz watch with date display. Water resistant to 30m.',
         price=135.00, currency='USD', quantity_available=60, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1541778480-fc1752bbc2a9?w=600&h=400&fit=crop&q=80'),

    # ── Watches — Women ───────────────────────────────────────────────────────
    dict(name='Diamond Coated Hand Watch for Women', category='watches', gender_target='women',
         description='Luxury diamond-coated watch with a slim case and refined bracelet strap. Quartz movement, mineral crystal glass.',
         price=210.00, currency='USD', quantity_available=40, unit='piece',
         market_type='both', origin_country='CA', is_featured=True,
         image_url='https://images.unsplash.com/photo-1451477334999-a9321157a431?w=600&h=400&fit=crop&q=80'),

    dict(name='Gold Coated Hand Watch for Women', category='watches', gender_target='women',
         description='Slim women\'s watch with gold-coated case and bracelet strap. Quartz movement, mineral crystal glass.',
         price=140.00, currency='USD', quantity_available=55, unit='piece',
         market_type='both', origin_country='CA',
         image_url='https://images.unsplash.com/photo-1604242692760-2f7b0c26856d?w=600&h=400&fit=crop&q=80'),
]

created_count = 0
for p in PRODUCTS:
    obj, c = Product.objects.get_or_create(name=p['name'], defaults=p)
    if c:
        created_count += 1
        print(f"  ✓ Created product: {obj.name}")
    else:
        print(f"  – Already exists: {obj.name}")
print(f"\nProducts: {created_count} created / {len(PRODUCTS) - created_count} already existed")

# ── 3. Forex Rates (CAD/UGX · CAD/KES · UGX/KES) ───────────────────────────
FOREX = [
    ('CAD', 'UGX', 2693.00),
    ('CAD', 'KES', 93.70),
    ('UGX', 'KES', 0.034780),
    # Reverse pairs
    ('UGX', 'CAD', 0.000371),
    ('KES', 'CAD', 0.010672),
    ('KES', 'UGX', 28.75),
]
for from_c, to_c, rate in FOREX:
    obj, c = ForexRate.objects.get_or_create(from_currency=from_c, to_currency=to_c,
                                              defaults={'rate': rate})
    if not c:
        obj.rate = rate
        obj.save()
    print(f"  {'Created' if c else 'Updated'} forex: {from_c}/{to_c} = {rate}")

# ── 4. Training Programs ──────────────────────────────────────────────────────
TRAINING = [
    dict(title='Import & Export Operations',
         category='trade',
         description='Master the fundamentals of cross-border import/export: documentation, RM registration, customs and compliance.',
         duration_hours=8, certificate_fee=500),
    dict(title='E-Commerce Business Setup & Management',
         category='enterprise',
         description='How to set up and run a successful online trade and e-commerce business. Registration, logistics, marketing.',
         duration_hours=6, certificate_fee=500),
]
for t in TRAINING:
    obj, c = TrainingProgram.objects.get_or_create(title=t['title'], defaults=t)
    print(f"  {'Created' if c else 'Exists'} training: {obj.title}")

# ── 5. TV Programs ────────────────────────────────────────────────────────────
TV = [
    dict(title='T&TG Global Trade Report',
         description='Weekly trade report covering import/export news across Canada, Uganda and Kenya.',
         broadcast_schedule='Every Monday', category='trade', is_active=True),
    dict(title='Farming Tech Weekly',
         description='The latest in agricultural technology and modern farming practices.',
         broadcast_schedule='Every Wednesday', category='farming', is_active=True),
    dict(title='Coffee & Trade',
         description='Exploring the coffee trade from Uganda and Kenya — cultivation, processing and global markets.',
         broadcast_schedule='Every Saturday', category='coffee', is_active=True),
    dict(title='T&TG Partner Spotlight',
         description='Monthly feature on T&TG partners and success stories from our three operating countries.',
         broadcast_schedule='Monthly', category='partnership', is_active=True),
]
for tv in TV:
    obj, c = TVProgram.objects.get_or_create(title=tv['title'], defaults=tv)
    print(f"  {'Created' if c else 'Exists'} TV program: {obj.title}")

print("\n✅ Seed data complete.")
print("   Run 'python manage.py migrate' first if you haven't already.")
