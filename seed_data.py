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
    dict(name='Robusta Green Coffee', category='coffee', gender_target='all',
         description='Premium Robusta green coffee beans sourced from Uganda. Rich, bold flavour profile ideal for espresso blends. Sold per kilogram.',
         price=28.00, currency='USD', quantity_available=500, unit='kg',
         market_type='both', origin_country='UG', is_featured=True),

    dict(name='Arabica Green Coffee', category='coffee', gender_target='all',
         description='High-altitude Arabica green coffee beans — smooth, nuanced flavour with bright acidity. Sourced from Uganda and Kenya.',
         price=35.00, currency='USD', quantity_available=400, unit='kg',
         market_type='both', origin_country='UG', is_featured=True),

    # ── Clothing — Men ────────────────────────────────────────────────────────
    dict(name='Men\'s Business Suit', category='clothing', gender_target='men',
         description='Premium two-piece business suit. Available in navy, charcoal and black. Tailored fit, wrinkle-resistant fabric. Sizes S–3XL.',
         price=180.00, currency='USD', quantity_available=80, unit='piece',
         market_type='both', origin_country='CA', is_featured=True),

    dict(name='Men\'s Formal Shirt', category='clothing', gender_target='men',
         description='Crisp formal cotton shirt. Available in white, light blue and grey. Button-down collar. Machine washable. Sizes S–3XL.',
         price=35.00, currency='USD', quantity_available=200, unit='piece',
         market_type='local', origin_country='CA'),

    dict(name='Men\'s T-Shirt', category='clothing', gender_target='men',
         description='Comfortable 100% cotton T-shirt. Available in multiple colours. Lightweight and breathable. Sizes S–3XL.',
         price=18.00, currency='USD', quantity_available=300, unit='piece',
         market_type='local', origin_country='CA'),

    dict(name='Men\'s Chino Trousers', category='clothing', gender_target='men',
         description='Smart chino trousers in stretch cotton blend. Slim fit. Available in khaki, navy and olive. Sizes 28–40 waist.',
         price=55.00, currency='USD', quantity_available=150, unit='piece',
         market_type='both', origin_country='CA'),

    # ── Clothing — Women ──────────────────────────────────────────────────────
    dict(name='Women\'s Formal Blouse', category='clothing', gender_target='women',
         description='Elegant formal blouse in premium polyester blend. Perfect for office or events. Available in white, blush and teal. Sizes XS–2XL.',
         price=42.00, currency='USD', quantity_available=180, unit='piece',
         market_type='both', origin_country='CA'),

    dict(name='Women\'s T-Shirt', category='clothing', gender_target='women',
         description='Lightweight women\'s T-shirt in soft cotton. Relaxed fit. Available in multiple pastel and classic colours. Sizes XS–2XL.',
         price=16.00, currency='USD', quantity_available=250, unit='piece',
         market_type='local', origin_country='CA'),

    dict(name='Women\'s Trousers', category='clothing', gender_target='women',
         description='Smart women\'s trousers in tailored fit. Stretch fabric for all-day comfort. Available in black, navy and cream. Sizes 6–18.',
         price=58.00, currency='USD', quantity_available=120, unit='piece',
         market_type='both', origin_country='CA'),

    # ── Clothing — Children ───────────────────────────────────────────────────
    dict(name='Children\'s School Shirt', category='clothing', gender_target='children',
         description='Durable school shirt for boys and girls. Easy-iron fabric. White and light blue. Ages 4–14.',
         price=12.00, currency='USD', quantity_available=350, unit='piece',
         market_type='local', origin_country='CA'),

    dict(name='Children\'s T-Shirt Pack (3)', category='clothing', gender_target='children',
         description='Pack of 3 colourful cotton T-shirts for children. Machine washable. Ages 2–12.',
         price=22.00, currency='USD', quantity_available=200, unit='pack',
         market_type='local', origin_country='CA'),

    # ── Shoes ─────────────────────────────────────────────────────────────────
    dict(name='Men\'s Leather Dress Shoes', category='shoes', gender_target='men',
         description='Classic leather dress shoes with rubber sole. Available in black and tan. Sizes 39–47.',
         price=95.00, currency='USD', quantity_available=100, unit='pair',
         market_type='both', origin_country='CA', is_featured=True),

    dict(name='Women\'s Heeled Shoes', category='shoes', gender_target='women',
         description='Elegant heeled court shoes in faux leather. Available in black, nude and red. Sizes 35–42.',
         price=75.00, currency='USD', quantity_available=90, unit='pair',
         market_type='both', origin_country='CA'),

    dict(name='Children\'s School Shoes', category='shoes', gender_target='children',
         description='Sturdy black school shoes with Velcro or lace-up fastening. Sizes 28–38.',
         price=35.00, currency='USD', quantity_available=160, unit='pair',
         market_type='local', origin_country='CA'),

    dict(name='Unisex Casual Sneakers', category='shoes', gender_target='all',
         description='Lightweight casual sneakers suitable for all. Breathable mesh upper. Available in white, black and grey. Sizes 35–47.',
         price=55.00, currency='USD', quantity_available=200, unit='pair',
         market_type='both', origin_country='CA'),

    # ── Watches ───────────────────────────────────────────────────────────────
    dict(name='Men\'s Stainless Steel Watch', category='watches', gender_target='men',
         description='Classic stainless steel quartz watch with date display. Water resistant to 30m. Silver and gold-tone bezels available.',
         price=120.00, currency='USD', quantity_available=70, unit='piece',
         market_type='both', origin_country='CA', is_featured=True),

    dict(name='Women\'s Elegant Watch', category='watches', gender_target='women',
         description='Slim women\'s watch with rose-gold tone case and leather strap. Quartz movement. Mineral crystal glass.',
         price=95.00, currency='USD', quantity_available=60, unit='piece',
         market_type='both', origin_country='CA'),

    dict(name='Children\'s Digital Watch', category='watches', gender_target='children',
         description='Durable digital watch with alarm, stopwatch and backlight. Waterproof. Rubber strap in fun colours. Ages 5–12.',
         price=22.00, currency='USD', quantity_available=150, unit='piece',
         market_type='local', origin_country='CA'),
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
    dict(title='Modern & Tech Farming',
         category='farming',
         description='Cutting-edge farming techniques including precision agriculture, drone technology and soil analytics.',
         duration_hours=12.5, certificate_fee=500),
    dict(title='Trade & e-Commerce Business Setup',
         category='enterprise',
         description='How to set up and run a successful online trade and e-commerce business. Registration, logistics, marketing.',
         duration_hours=6, certificate_fee=500),
    dict(title='Import & Export Operations',
         category='trade',
         description='Master the fundamentals of cross-border import/export: documentation, RM registration, customs and compliance.',
         duration_hours=8, certificate_fee=500),
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
