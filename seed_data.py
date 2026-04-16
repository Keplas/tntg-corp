"""
T&TG Trade Corporation — Seed Data Script
==========================================
Run with:  python manage.py shell < seed_data.py
  OR:      python seed_data.py   (if run from project root with Django configured)

Populates the database with realistic sample data for all apps.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta, datetime

# ── Bootstrap Django if run directly ──────────────────────────────────────────
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tntg_corp.settings")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    django.setup()

from django.utils import timezone

from accounts.models import CustomUser, AvonPointTransaction
from marketplace.models import Product, Order, ProductReview
from services.models import ForexRate, InsurancePolicy, BrokerageAccount, ContactInquiry
from training.models import TrainingProgram, TVProgram, Enrollment

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def banner(title):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")

def ok(msg):
    print(f"  ✓  {msg}")

def skip(msg):
    print(f"  –  {msg} (already exists)")


# ══════════════════════════════════════════════════════════════════════════════
# 1. USERS
# ══════════════════════════════════════════════════════════════════════════════
banner("1 · USERS")

USERS = [
    # username, password, first, last, email, phone, country, city, market, role, is_partner, is_verified, avon, is_staff, is_super
    ("admin",      "admin123",    "Tom",     "Ssembiito",   "tom@tntg.ca",          "+1-416-832-3512", "CA", "Toronto",     "both",          "both",    False, True,  2500.00, True,  True),
    ("edgar_k",    "pass1234",    "Edgar",   "Kitayimbwa",  "edgar@tntg.ca",         "+1-416-555-0101", "CA", "Toronto",     "both",          "seller",  True,  True,  1800.50, False, False),
    ("musana_f",   "pass1234",    "Musana",  "Francis",     "musana@tntg.ca",        "+256-700-123456", "UG", "Kampala",     "both",          "both",    True,  True,  980.00,  False, False),
    ("alice_nl",   "pass1234",    "Alice",   "Van der Berg","alice@trade.nl",        "+31-20-555-0200", "NL", "Amsterdam",   "international", "buyer",   False, True,  450.75,  False, False),
    ("james_ke",   "pass1234",    "James",   "Mwangi",      "james@trade.ke",        "+254-722-000111", "KE", "Nairobi",     "local",         "buyer",   False, True,  320.00,  False, False),
    ("yuki_jp",    "pass1234",    "Yuki",    "Tanaka",      "yuki@trade.jp",         "+81-3-5555-0300", "JP", "Tokyo",       "international", "buyer",   False, False, 0.00,    False, False),
    ("robert_us",  "pass1234",    "Robert",  "Johnson",     "robert@trade.us",       "+1-212-555-0404", "US", "New York",    "international", "partner", True,  True,  3200.00, False, False),
    ("sarah_ug",   "pass1234",    "Sarah",   "Namukasa",    "sarah@trade.ug",        "+256-752-987654", "UG", "Entebbe",     "local",         "seller",  False, True,  760.25,  False, False),
    ("piet_nl",    "pass1234",    "Piet",    "De Boer",     "piet@globaltrade.nl",   "+31-10-555-0505", "NL", "Rotterdam",   "international", "partner", True,  True,  5100.00, False, False),
    ("grace_ke",   "pass1234",    "Grace",   "Wanjiku",     "grace@keatrade.ke",     "+254-733-000222", "KE", "Mombasa",     "local",         "seller",  False, False, 0.00,    False, False),
    ("demo_buyer", "pass1234",    "Demo",    "Buyer",       "demo@tntgtest.ca",      "+1-416-000-0000", "CA", "Mississauga", "local",         "buyer",   False, False, 125.50,  False, False),
]

created_users = {}
for (username, password, first, last, email, phone, country, city,
     market, role, is_partner, is_verified, avon, is_staff, is_super) in USERS:

    if CustomUser.objects.filter(username=username).exists():
        skip(f"User '{username}'")
        created_users[username] = CustomUser.objects.get(username=username)
        continue

    if is_super:
        u = CustomUser.objects.create_superuser(username, email, password)
    else:
        u = CustomUser.objects.create_user(username, email, password)

    u.first_name      = first
    u.last_name       = last
    u.phone           = phone
    u.country         = country
    u.city            = city
    u.market_type     = market
    u.user_role       = role
    u.is_partner      = is_partner
    u.is_verified     = is_verified
    u.avon_points     = Decimal(str(avon))
    u.is_staff        = is_staff
    u.is_superuser    = is_super
    u.term_preference = "long" if is_partner else "short"
    u.business_description = (
        f"{first} {last} — trading on T&TG platform. "
        f"Specialises in {'import/export and partnership' if is_partner else 'buying and selling on the marketplace'}."
    )
    u.save()
    ok(f"User '{username}'  [{u.unique_id}]")
    created_users[username] = u


# ══════════════════════════════════════════════════════════════════════════════
# 2. FOREX RATES
# ══════════════════════════════════════════════════════════════════════════════
banner("2 · FOREX RATES")

FOREX = [
    # from_currency, to_currency, rate
    ("USD", "CAD",  Decimal("1.3812")),
    ("USD", "UGX",  Decimal("3720.00")),
    ("USD", "EUR",  Decimal("0.9148")),
    ("USD", "GBP",  Decimal("0.7870")),
    ("USD", "KES",  Decimal("129.45")),
    ("USD", "JPY",  Decimal("153.82")),
    ("USD", "NLD",  Decimal("0.9148")),   # Netherlands uses EUR
    ("EUR", "USD",  Decimal("1.0934")),
    ("EUR", "GBP",  Decimal("0.8601")),
    ("GBP", "USD",  Decimal("1.2711")),
    ("CAD", "USD",  Decimal("0.7240")),
    ("KES", "USD",  Decimal("0.0077")),
    ("UGX", "USD",  Decimal("0.000269")),
    ("JPY", "USD",  Decimal("0.0065")),
    ("BTC", "USD",  Decimal("67430.00")),
    ("ETH", "USD",  Decimal("3280.00")),
    ("XAU", "USD",  Decimal("2345.80")),  # Gold spot
    ("XAG", "USD",  Decimal("29.42")),    # Silver spot
]

for fc, tc, rate in FOREX:
    obj, created = ForexRate.objects.get_or_create(
        from_currency=fc, to_currency=tc,
        defaults={"rate": rate}
    )
    if created:
        ok(f"{fc}/{tc} = {rate}")
    else:
        skip(f"{fc}/{tc}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
banner("3 · PRODUCTS")

admin_user = created_users.get("admin")
edgar      = created_users.get("edgar_k")
sarah      = created_users.get("sarah_ug")
piet       = created_users.get("piet_nl")

PRODUCTS = [
    # name, category, description, price, currency, qty, unit, market, seller_key, is_active, is_featured, origin
    (
        "Apple MacBook Pro M3 14\"",
        "electronics",
        "The most powerful MacBook Pro ever. Features Apple M3 chip with 16GB unified memory, 512GB SSD storage, Liquid Retina XDR display, and up to 18 hours of battery life. Perfect for developers, designers, and creative professionals.",
        2499.00, "USD", 20, "unit", "both", "edgar_k", True, True, "US"
    ),
    (
        "Apple MacBook Air M2",
        "electronics",
        "Supercharged by the M2 chip, MacBook Air is impossibly thin and features a stunning 13.6-inch Liquid Retina display with 8GB RAM and 256GB SSD. Fanless design, all-day battery.",
        1299.00, "USD", 35, "unit", "both", "edgar_k", True, True, "US"
    ),
    (
        "Dell XPS 15 Laptop",
        "electronics",
        "Dell XPS 15 featuring Intel Core i7-13700H, 32GB DDR5 RAM, 1TB NVMe SSD, and a stunning 15.6\" OLED touchscreen. Premium build quality with Thunderbolt 4, ideal for business and creative work.",
        1899.00, "USD", 12, "unit", "international", "edgar_k", True, True, "US"
    ),
    (
        "HP LaserJet Pro MFP 4301",
        "electronics",
        "Professional all-in-one laser printer with print, scan, copy and fax. Wireless printing, automatic duplex, 600dpi resolution, 40ppm print speed. Ideal for small to medium businesses.",
        399.00, "USD", 45, "unit", "both", "edgar_k", True, False, "US"
    ),
    (
        "Canon EOS R50 Mirrorless Camera",
        "electronics",
        "24.2 MP APS-C CMOS sensor, DIGIC X image processor, 4K UHD video recording, Dual Pixel CMOS AF II autofocus. Compact and lightweight — perfect for photography, content creation and vlogging.",
        799.00, "USD", 18, "unit", "both", "edgar_k", True, False, "JP"
    ),
    (
        "Samsung 65\" QLED 4K Smart TV",
        "electronics",
        "65-inch Quantum Dot display with 4K resolution, HDR10+, Dolby Atmos audio. Tizen Smart TV OS with built-in streaming. Slim design with One Connect Box.",
        1199.00, "USD", 8, "unit", "both", "edgar_k", True, False, "KR"
    ),
    (
        "Logitech MX Master 3S Mouse",
        "electronics",
        "Advanced wireless mouse with ultra-fast MagSpeed scrolling, 8K DPI sensor, Quiet Click buttons. Compatible with Windows and macOS. Up to 70 days battery life on full charge.",
        99.00, "USD", 100, "unit", "both", "edgar_k", True, False, "US"
    ),
    # ── COFFEE ──────────────────────────────────────────────────────────────
    (
        "Organic Green Arabica Coffee Beans",
        "coffee",
        "Premium single-origin green Arabica coffee beans sourced from the highlands of Uganda and Kenya. Altitude grown at 1,500–2,200m. Washed process. Perfect for home and commercial roasters. Smooth acidity, floral and citrus notes.",
        12.00, "USD", 800, "kg", "both", "sarah_ug", True, True, "UG"
    ),
    (
        "Roasted Arabica Coffee — Medium Roast",
        "coffee",
        "Our flagship roasted Arabica blend. Medium roast with rich body, balanced acidity and notes of dark chocolate, caramel and dried fruit. Roasted fresh-to-order at our T&TG roasting facility. Sold per kg.",
        45.00, "USD", 300, "kg", "both", "sarah_ug", True, True, "UG"
    ),
    (
        "Roasted Arabica Coffee — Dark Roast",
        "coffee",
        "Bold, full-bodied dark roast with low acidity. Notes of dark chocolate, molasses and a smoky finish. Ideal for espresso and French press. Freshly roasted and vacuum sealed for maximum freshness.",
        47.00, "USD", 250, "kg", "both", "sarah_ug", True, False, "UG"
    ),
    (
        "Cold Brew Coffee Concentrate",
        "coffee",
        "Ready-to-dilute cold brew concentrate made from our premium Arabica beans. Steeped for 20 hours for maximum smoothness. 1 litre makes up to 8 servings. No bitterness, naturally sweet finish.",
        18.00, "USD", 200, "litre", "local", "sarah_ug", True, False, "UG"
    ),
    (
        "Specialty Espresso Blend (250g)",
        "coffee",
        "Our premium espresso blend — a curated mix of Ugandan and Kenyan Arabica. Delivers a rich crema, intense aroma and long aftertaste. Pre-ground or whole bean options available.",
        14.00, "USD", 400, "pack", "both", "sarah_ug", True, False, "UG"
    ),
    # ── PHARMACEUTICALS ──────────────────────────────────────────────────────
    (
        "Pharmaceutical Grade Multi-Vitamins",
        "pharmaceuticals",
        "Complete daily multi-vitamin pack for adults — 90 capsules per bottle. Contains Vitamins A, B-complex, C, D3, E, K2, Zinc and Magnesium. GMP certified, pharmaceutical grade quality.",
        29.99, "USD", 200, "bottle", "both", "admin", True, False, "CA"
    ),
    (
        "Omega-3 Fish Oil Capsules (90ct)",
        "pharmaceuticals",
        "High-potency Omega-3 supplement — 1000mg per softgel, 90 capsules. Supports heart, brain and joint health. Molecularly distilled for purity. No fishy aftertaste.",
        24.99, "USD", 150, "bottle", "both", "admin", True, False, "CA"
    ),
    (
        "Hand Sanitizer — 500ml (Bulk)",
        "pharmaceuticals",
        "WHO-recommended formulation 80% ethanol hand sanitizer. Kills 99.9% of germs. Moisturising formula with aloe vera. Suitable for hospitals, offices, schools and homes. Bulk packaging — 500ml.",
        8.50, "USD", 1000, "bottle", "both", "admin", True, False, "NL"
    ),
    # ── AGRICULTURE ──────────────────────────────────────────────────────────
    (
        "Organic Maize (White Corn) — 50kg",
        "agriculture",
        "Premium quality white maize/corn, sun-dried and cleaned. Moisture content below 14%. Suitable for human consumption, animal feed and industrial processing. Sourced from Ugandan highland farms.",
        35.00, "USD", 500, "bag", "both", "sarah_ug", True, False, "UG"
    ),
    (
        "Arabica Coffee Seedlings (per 100)",
        "agriculture",
        "Healthy, disease-resistant Arabica coffee seedlings, 3–4 months old. Ready for transplanting. Grown from certified seed stock. Ideal for establishing new coffee farms at altitudes above 1,200m.",
        55.00, "USD", 200, "batch", "local", "sarah_ug", True, False, "UG"
    ),
    (
        "Premium Sunflower Oil — 5L",
        "agriculture",
        "Cold-pressed, refined sunflower oil. High smoke point (230°C). Rich in Vitamin E. Suitable for frying, baking and salads. Sourced from certified farms in East Africa.",
        12.00, "USD", 300, "bottle", "both", "sarah_ug", True, False, "KE"
    ),
    # ── TEXTILES ─────────────────────────────────────────────────────────────
    (
        "African Print Fabric — per metre",
        "textiles",
        "High-quality 100% cotton African wax print fabric. Vibrant, colourfast designs. Width: 115cm. Suitable for clothing, accessories and home décor. Sourced from certified weavers in Uganda and Kenya.",
        8.00, "USD", 1500, "metre", "both", "sarah_ug", True, False, "UG"
    ),
    # ── MACHINERY ──────────────────────────────────────────────────────────────
    (
        "Commercial Coffee Roasting Machine (5kg)",
        "machinery",
        "Professional drum roaster, 5kg capacity per batch. Digital temperature control, chaff collector, cooling tray. 304 stainless steel drum. Suitable for small to medium coffee roasting businesses.",
        3200.00, "USD", 5, "unit", "international", "piet_nl", True, True, "NL"
    ),
    (
        "Solar Water Pump System",
        "machinery",
        "Complete off-grid solar water pumping system: 300W solar panel, 24V submersible pump, MPPT controller, wiring kit. Flow rate 3000 L/hour. Ideal for irrigation, livestock and rural water supply.",
        850.00, "USD", 25, "unit", "both", "piet_nl", True, False, "NL"
    ),
]

created_products = {}
for row in PRODUCTS:
    (name, cat, desc, price, currency, qty, unit,
     market, seller_key, is_active, is_featured, origin) = row

    seller = created_users.get(seller_key)
    obj, created = Product.objects.get_or_create(
        name=name,
        defaults={
            "category":           cat,
            "description":        desc,
            "price":              Decimal(str(price)),
            "currency":           currency,
            "quantity_available": qty,
            "unit":               unit,
            "market_type":        market,
            "seller":             seller,
            "origin_country":     origin,
            "is_active":          is_active,
            "is_featured":        is_featured,
        }
    )
    if created:
        ok(f"Product '{name}'  [{cat}]  ${price}")
    else:
        skip(f"Product '{name}'")
    created_products[name] = obj


# ══════════════════════════════════════════════════════════════════════════════
# 4. ORDERS
# ══════════════════════════════════════════════════════════════════════════════
banner("4 · ORDERS")

macbook   = created_products.get("Apple MacBook Pro M3 14\"")
arabica   = created_products.get("Roasted Arabica Coffee — Medium Roast")
green_cof = created_products.get("Organic Green Arabica Coffee Beans")
printer   = created_products.get("HP LaserJet Pro MFP 4301")
vitamins  = created_products.get("Pharmaceutical Grade Multi-Vitamins")
roaster   = created_products.get("Commercial Coffee Roasting Machine (5kg)")
solar     = created_products.get("Solar Water Pump System")
fabric    = created_products.get("African Print Fabric — per metre")

ORDERS = [
    # buyer_key, product, qty, delivery, dest_country, dest_address, days_ahead, status, referred_by, ref_id
    ("alice_nl",   macbook,   2,  "express",  "Netherlands", "Keizersgracht 123, Amsterdam 1015CW",         10, "accepted",     "",           ""),
    ("james_ke",   arabica,   10, "ordinary", "Kenya",       "Moi Avenue 45, Nairobi 00100",                21, "processing",   "",           ""),
    ("robert_us",  macbook,   5,  "express",  "USA",         "5th Avenue, Suite 800, New York, NY 10001",   7,  "accepted",     "Piet De Boer","TG00009"),
    ("yuki_jp",    roaster,   1,  "express",  "Japan",       "Shinjuku-ku, Tokyo 160-0022",                 14, "pending",      "",           ""),
    ("demo_buyer", vitamins,  3,  "ordinary", "Canada",      "123 Main St, Mississauga, ON L5B 2T4",        30, "delivered",    "",           ""),
    ("sarah_ug",   solar,     2,  "ordinary", "Uganda",      "Plot 44 Kampala Road, Entebbe",               45, "processing",   "",           ""),
    ("musana_f",   green_cof, 50, "ordinary", "Uganda",      "Nakasero Hill, Kampala",                      28, "accepted",     "",           ""),
    ("alice_nl",   arabica,   5,  "express",  "Netherlands", "Prins Hendrikkade 88, Rotterdam 3072",        5,  "shipped",      "Piet De Boer","TG00009"),
    ("james_ke",   fabric,    100,"ordinary", "Kenya",       "Industrial Area, Nairobi",                    60, "pending",      "",           ""),
    ("demo_buyer", printer,   1,  "ordinary", "Canada",      "456 Elm Street, Toronto, ON M4C 1L8",         20, "accepted",     "",           ""),
    ("robert_us",  green_cof, 200,"express",  "USA",         "Port Newark, Elizabeth, NJ 07201",            15, "processing",   "Robert Johnson","TG00007"),
    ("grace_ke",   arabica,   8,  "ordinary", "Kenya",       "Nyali, Mombasa 80109",                        35, "pending",      "",           ""),
]

for (buyer_key, product, qty, delivery, dest_country,
     dest_address, days_ahead, status, referred_by, ref_id) in ORDERS:

    if product is None:
        skip(f"Order for missing product (buyer={buyer_key})")
        continue

    buyer = created_users.get(buyer_key)
    if buyer is None:
        skip(f"Order — buyer '{buyer_key}' not found")
        continue

    total = product.price * qty
    pts   = Decimal(str(float(total) / (8.5 if referred_by else 5.5)))

    if not Order.objects.filter(buyer=buyer, product=product, quantity=qty).exists():
        Order.objects.create(
            buyer               = buyer,
            product             = product,
            order_type          = "buy",
            quantity            = qty,
            total_price         = total,
            delivery_type       = delivery,
            destination_country = dest_country,
            destination_address = dest_address,
            desired_arrival_date= date.today() + timedelta(days=days_ahead),
            status              = status,
            referred_by         = referred_by,
            referrer_unique_id  = ref_id,
            avon_points_earned  = pts,
        )
        ok(f"Order: {buyer_key} → {product.name[:35]}  qty={qty}  [{status}]")
    else:
        skip(f"Order: {buyer_key} → {product.name[:35]}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. PRODUCT REVIEWS
# ══════════════════════════════════════════════════════════════════════════════
banner("5 · PRODUCT REVIEWS")

REVIEWS = [
    ("alice_nl",   "Apple MacBook Pro M3 14\"",                    5, "Absolutely exceptional machine. The M3 chip is blazing fast and the display is gorgeous. Arrived perfectly packaged. T&TG delivery was smooth."),
    ("robert_us",  "Apple MacBook Pro M3 14\"",                    5, "Ordered 5 units for our team. All arrived in perfect condition via express delivery. Great pricing compared to local suppliers."),
    ("james_ke",   "Roasted Arabica Coffee — Medium Roast",        5, "Best coffee I have had in years. The flavour profile is outstanding — chocolate and fruit notes just as described. Will order monthly."),
    ("alice_nl",   "Roasted Arabica Coffee — Medium Roast",        4, "Very smooth and aromatic. Slight delay on express shipping but the quality makes up for it. Already ordered again."),
    ("demo_buyer", "Pharmaceutical Grade Multi-Vitamins",          4, "Good quality vitamins. Packaging was excellent and delivery was on time. Would appreciate more flavour options."),
    ("demo_buyer", "HP LaserJet Pro MFP 4301",                     5, "Works perfectly out of the box. Wireless setup was easy and print quality is sharp. Great value for a business printer."),
    ("musana_f",   "Organic Green Arabica Coffee Beans",           5, "As a coffee trader myself, I can confirm these beans are top quality. Consistent size, low defects, beautiful green colour."),
    ("sarah_ug",   "Solar Water Pump System",                      4, "Installed on our farm — working well after 3 months. Excellent flow rate. The MPPT controller is efficient even on cloudy days."),
]

for (user_key, product_name, rating, comment) in REVIEWS:
    user    = created_users.get(user_key)
    product = created_products.get(product_name)
    if user and product:
        if not ProductReview.objects.filter(user=user, product=product).exists():
            ProductReview.objects.create(user=user, product=product, rating=rating, comment=comment)
            ok(f"Review: {user_key} → {product_name[:40]}  ({'★'*rating})")
        else:
            skip(f"Review: {user_key} → {product_name[:30]}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. AVON POINT TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
banner("6 · AVON POINT TRANSACTIONS")

today = date.today()

AVON_TX = [
    # user_key, type, points, quarter, status, days_ago, description
    ("admin",      "earn_purchase", 454.55, "",   "completed", 45, "Earned from Order #1 — Apple MacBook Pro M3"),
    ("admin",      "earn_referral", 294.12, "",   "completed", 30, "Referral bonus — Robert Johnson order"),
    ("alice_nl",   "earn_purchase", 454.55, "",   "completed", 20, "Earned from Order #1 — MacBook Pro purchase"),
    ("alice_nl",   "earn_referral", 105.88, "",   "completed", 10, "Referral bonus — Arabica Coffee order"),
    ("alice_nl",   "sell_order",    200.00, "Q2", "pending",    5, "Sell order 200 pts — Q2"),
    ("james_ke",   "earn_purchase", 163.64, "",   "completed", 15, "Earned from Order #2 — Arabica Coffee 10kg"),
    ("james_ke",   "earn_purchase",  21.82, "",   "completed",  8, "Earned from Order #9 — African Print Fabric"),
    ("robert_us",  "earn_referral", 564.71, "",   "completed", 18, "Referral earned — MacBook order (5 units)"),
    ("robert_us",  "earn_purchase", 836.36, "",   "completed", 12, "Earned from Order #11 — Green Coffee Beans 200kg"),
    ("robert_us",  "sell_order",   1000.00, "Q3", "pending",    3, "Sell order 1000 pts — Q3"),
    ("musana_f",   "earn_purchase", 327.27, "",   "completed", 25, "Earned from Order #7 — Green Coffee Beans 50kg"),
    ("demo_buyer", "earn_purchase",  16.36, "",   "completed", 30, "Earned from Order #5 — Multi-Vitamins x3"),
    ("demo_buyer", "earn_purchase",  43.64, "",   "completed", 15, "Earned from Order #10 — HP Printer"),
    ("sarah_ug",   "earn_purchase", 185.45, "",   "completed", 20, "Earned from Order #6 — Solar Pump x2"),
    ("sarah_ug",   "sell_order",    100.00, "Q1", "processing", 2, "Sell order 100 pts — Q1"),
    ("piet_nl",    "earn_referral", 376.47, "",   "completed", 10, "Referral bonus — MacBook & Coffee orders"),
    ("piet_nl",    "earn_purchase",2000.00, "",   "completed", 60, "Earned from Commercial Coffee Roaster sale"),
    ("piet_nl",    "sell_order",   1500.00, "Q4", "pending",    7, "Sell order 1500 pts — Q4"),
    ("edgar_k",    "earn_purchase", 800.00, "",   "completed", 90, "Platform earnings — product listings Q1"),
    ("edgar_k",    "redeem_insurance", 100.00, "", "completed", 30, "Insurance premium payment — Trade Insurance"),
]

for (user_key, tx_type, pts, quarter, status, days_ago, description) in AVON_TX:
    user = created_users.get(user_key)
    if user:
        if not AvonPointTransaction.objects.filter(user=user, description=description).exists():
            min_date = (today + timedelta(days=90)) if tx_type == "sell_order" else None
            AvonPointTransaction.objects.create(
                user             = user,
                transaction_type = tx_type,
                points           = Decimal(str(pts)),
                quarter          = quarter,
                status           = status,
                description      = description,
                min_execution_date = min_date,
            )
            ok(f"AvonTx: {user_key}  {tx_type}  {pts} pts  [{status}]")
        else:
            skip(f"AvonTx: {user_key}  {description[:40]}")


# ══════════════════════════════════════════════════════════════════════════════
# 7. INSURANCE POLICIES
# ══════════════════════════════════════════════════════════════════════════════
banner("7 · INSURANCE POLICIES")

INSURANCE = [
    # user_key, policy_type, policy_number, coverage, premium, start_days_ago, duration_days, status
    ("admin",     "trade",    "TI-2026-001", 50000.00, 250.00,  60, 365, "active"),
    ("edgar_k",   "trade",    "TI-2026-002", 30000.00, 150.00,  30, 365, "active"),
    ("musana_f",  "health",   "HI-2026-003", 15000.00,  80.00,  45, 365, "active"),
    ("alice_nl",  "cargo",    "CI-2026-004", 25000.00, 120.00,  15, 180, "active"),
    ("robert_us", "business", "BI-2026-005",100000.00, 500.00,  90, 365, "active"),
    ("piet_nl",   "trade",    "TI-2026-006", 75000.00, 375.00, 120, 365, "active"),
    ("james_ke",  "health",   "HI-2026-007", 10000.00,  50.00,  10, 365, "pending"),
    ("sarah_ug",  "life",     "LI-2026-008", 20000.00, 100.00,  5,  365, "pending"),
    ("demo_buyer","health",   "HI-2026-009",  8000.00,  40.00, 180, 365, "active"),
]

for (user_key, policy_type, policy_number, coverage,
     premium, start_days_ago, duration_days, status) in INSURANCE:

    user = created_users.get(user_key)
    if user and not InsurancePolicy.objects.filter(policy_number=policy_number).exists():
        start = date.today() - timedelta(days=start_days_ago)
        InsurancePolicy.objects.create(
            user            = user,
            policy_type     = policy_type,
            policy_number   = policy_number,
            coverage_amount = Decimal(str(coverage)),
            premium         = Decimal(str(premium)),
            start_date      = start,
            end_date        = start + timedelta(days=duration_days),
            status          = status,
            description     = f"{policy_type.title()} insurance policy for {user.get_full_name()}",
        )
        ok(f"Policy {policy_number}  [{policy_type}]  {user_key}  [{status}]")
    else:
        skip(f"Policy {policy_number}")


# ══════════════════════════════════════════════════════════════════════════════
# 8. BROKERAGE ACCOUNTS
# ══════════════════════════════════════════════════════════════════════════════
banner("8 · BROKERAGE ACCOUNTS")

BROKERAGE = [
    # user_key, account_number, account_type, balance, currency, status
    ("admin",     "BRK-CA-00001", "forex",        5000.00, "USD", "active"),
    ("edgar_k",   "BRK-CA-00002", "stocks",       2500.00, "USD", "active"),
    ("piet_nl",   "BRK-NL-00003", "forex",       12000.00, "EUR", "active"),
    ("robert_us", "BRK-US-00004", "commodities",  8000.00, "USD", "active"),
    ("musana_f",  "BRK-UG-00005", "forex",        1200.00, "USD", "active"),
    ("alice_nl",  "BRK-NL-00006", "crypto",       3500.00, "USD", "active"),
    ("james_ke",  "BRK-KE-00007", "forex",         500.00, "USD", "pending"),
    ("demo_buyer","BRK-CA-00008", "stocks",          0.00, "USD", "pending"),
]

for (user_key, account_number, account_type, balance, currency, status) in BROKERAGE:
    user = created_users.get(user_key)
    if user and not BrokerageAccount.objects.filter(account_number=account_number).exists():
        BrokerageAccount.objects.create(
            user           = user,
            account_number = account_number,
            account_type   = account_type,
            balance        = Decimal(str(balance)),
            currency       = currency,
            status         = status,
        )
        ok(f"Brokerage {account_number}  [{account_type}]  ${balance}  [{status}]")
    else:
        skip(f"Brokerage {account_number}")


# ══════════════════════════════════════════════════════════════════════════════
# 9. TRAINING PROGRAMS
# ══════════════════════════════════════════════════════════════════════════════
banner("9 · TRAINING PROGRAMS")

TRAINING = [
    # title, category, description, duration_hours, cert_fee, is_free
    (
        "Modern & Tech Farming Fundamentals",
        "farming",
        "Comprehensive introduction to technology-driven agriculture. Covers precision farming, GPS-guided equipment, soil sensors, drone monitoring, drip irrigation systems, and sustainable land management. Combines theory with practical case studies from East African farms.",
        12.5, 500.00, True
    ),
    (
        "Advanced Coffee Cultivation & Roasting",
        "farming",
        "From seed to cup: in-depth training on Arabica coffee cultivation at altitude, harvesting best practices, wet and dry processing, green bean grading, roasting science and quality cupping. Designed for farmers, roasters and traders.",
        8.0, 500.00, True
    ),
    (
        "Aquaponics & Greenhouse Systems",
        "farming",
        "Modern food production using aquaponics (fish + vegetables) and controlled greenhouse environments. Covers system design, nutrient management, fish species selection, climate control and commercial-scale operations.",
        10.0, 500.00, True
    ),
    (
        "Corporate Mid-Market Enterprise Strategy",
        "enterprise",
        "Designed for business leaders and T&TG partners. Covers corporate governance, strategic planning, financial modelling, partnership structuring, mid-market M&A principles, and scaling operations across multiple countries. Includes real T&TG case studies.",
        20.0, 2000.00, True
    ),
    (
        "Import & Export Operations",
        "enterprise",
        "Step-by-step guide to international trade: documentation (Bill of Lading, Commercial Invoice, Certificate of Origin), Incoterms 2020, customs clearance, HS codes, trade financing, letters of credit, and managing cross-border logistics through T&TG partner networks.",
        8.0, 500.00, True
    ),
    (
        "E-Commerce Business Setup & Management",
        "enterprise",
        "How to register and operate a successful online business on the T&TG platform and beyond. Covers marketplace dynamics, pricing strategy, product listing optimisation, customer service, order fulfilment, and using Avon Points to grow your business.",
        6.0, 500.00, True
    ),
    (
        "Financial Services & Investment Essentials",
        "financial",
        "Master the fundamentals of personal and business finance: forex trading basics, reading financial statements, building diversified investment portfolios, understanding insurance products, managing risk, and using T&TG Brokerage tools. Required for international market eligibility.",
        15.0, 1500.00, True
    ),
    (
        "Forex Trading & Currency Management",
        "financial",
        "Practical forex training using T&TG Brokerage platform. Covers technical and fundamental analysis, reading charts, managing positions, cross-currency transactions in USD/CAD/UGX/KES/EUR/JPY, and using T&TG Avon Points as collateral.",
        12.0, 1500.00, True
    ),
    (
        "Insurance & Risk Management",
        "financial",
        "Understand how insurance products work, how to select the right policies for trade, health, cargo and life, how to file claims, and how to use Avon Points to offset premium costs. Covers all T&TG insurance products in detail.",
        6.0, 500.00, True
    ),
    (
        "Investment Portfolio & Real Estate",
        "financial",
        "Build and manage a diversified investment portfolio. Covers stocks, commodities, cryptocurrency basics, real estate investment using Avon Points, REITs, and how T&TG manages strategic investments for long-term growth.",
        10.0, 2000.00, True
    ),
]

created_programs = {}
for (title, cat, desc, duration, cert_fee, is_free) in TRAINING:
    obj, created = TrainingProgram.objects.get_or_create(
        title=title,
        defaults={
            "category":        cat,
            "description":     desc,
            "duration_hours":  Decimal(str(duration)),
            "certificate_fee": Decimal(str(cert_fee)),
            "is_free":         is_free,
            "is_active":       True,
        }
    )
    if created:
        ok(f"Training '{title[:55]}'  [{cat}]")
    else:
        skip(f"Training '{title[:55]}'")
    created_programs[title] = obj


# ══════════════════════════════════════════════════════════════════════════════
# 10. TV PROGRAMS
# ══════════════════════════════════════════════════════════════════════════════
banner("10 · TV PROGRAMS")

TV = [
    # title, description, schedule, category, is_live
    (
        "T&TG Global Trade Report",
        "Weekly deep-dive into global trade trends, commodity prices, shipping rates and market insights across our 6 operating countries. Features expert analysts, partner company spotlights, and T&TG platform updates. Essential viewing for all marketplace participants.",
        "Every Monday — 18:00 UTC",
        "Business & Trade",
        False
    ),
    (
        "Farming Tech Weekly",
        "Showcasing the latest innovations in agricultural technology — precision farming, drone applications, soil science, aquaponics, and sustainable practices across Africa and Asia. Includes farm visits, product demos and farmer interviews.",
        "Every Wednesday — 17:00 UTC",
        "Agriculture & Technology",
        False
    ),
    (
        "Investment Masterclass Live",
        "Expert-led live sessions on forex trading, stock markets, cryptocurrency, real estate investment and building diversified portfolios using T&TG Brokerage tools and Avon Points. Q&A with our investment team.",
        "Every Friday — 19:00 UTC",
        "Finance & Investment",
        True
    ),
    (
        "Coffee Culture & Trade",
        "Explore the world of specialty coffee — from East African highlands to global markets. Episodes cover cultivation, processing, roasting, cupping, barista skills, and the economics of the global coffee trade.",
        "Every Saturday — 10:00 UTC",
        "Food & Agriculture",
        False
    ),
    (
        "T&TG Partner Spotlight",
        "Monthly deep-dive featuring T&TG partner companies from Canada, Uganda, Netherlands, USA, Kenya and Japan. Interviews with founders, business case studies, and collaboration opportunities for new partners.",
        "First Sunday of every month — 15:00 UTC",
        "Business & Partnerships",
        False
    ),
    (
        "Forex & Currency Live",
        "Daily pre-market briefing covering USD/CAD, USD/UGX, EUR/USD, GBP/USD, USD/KES and USD/JPY rates. Technical analysis, key economic events of the day, and trading opportunities on T&TG Brokerage.",
        "Every weekday — 07:00 UTC",
        "Forex & Markets",
        True
    ),
]

for (title, desc, schedule, category, is_live) in TV:
    obj, created = TVProgram.objects.get_or_create(
        title=title,
        defaults={
            "description":        desc,
            "broadcast_schedule": schedule,
            "category":           category,
            "is_live":            is_live,
            "is_active":          True,
        }
    )
    if created:
        ok(f"TV  '{title[:55]}'  [{'LIVE' if is_live else 'Scheduled'}]")
    else:
        skip(f"TV  '{title[:55]}'")


# ══════════════════════════════════════════════════════════════════════════════
# 11. ENROLLMENTS
# ══════════════════════════════════════════════════════════════════════════════
banner("11 · TRAINING ENROLLMENTS")

ENROLLMENTS = [
    # user_key, program_title, status, progress
    ("alice_nl",   "Financial Services & Investment Essentials",  "in_progress",  65),
    ("alice_nl",   "Import & Export Operations",                  "completed",   100),
    ("james_ke",   "Modern & Tech Farming Fundamentals",          "enrolled",      0),
    ("james_ke",   "Advanced Coffee Cultivation & Roasting",      "in_progress",  40),
    ("robert_us",  "Corporate Mid-Market Enterprise Strategy",    "certified",   100),
    ("robert_us",  "Financial Services & Investment Essentials",  "certified",   100),
    ("musana_f",   "Advanced Coffee Cultivation & Roasting",      "completed",   100),
    ("musana_f",   "Import & Export Operations",                  "in_progress",  80),
    ("piet_nl",    "Corporate Mid-Market Enterprise Strategy",    "certified",   100),
    ("piet_nl",    "Forex Trading & Currency Management",         "in_progress",  55),
    ("sarah_ug",   "Modern & Tech Farming Fundamentals",          "completed",   100),
    ("sarah_ug",   "Advanced Coffee Cultivation & Roasting",      "certified",   100),
    ("edgar_k",    "E-Commerce Business Setup & Management",      "certified",   100),
    ("edgar_k",    "Financial Services & Investment Essentials",  "in_progress",  90),
    ("demo_buyer", "Modern & Tech Farming Fundamentals",          "enrolled",      0),
    ("yuki_jp",    "Import & Export Operations",                  "enrolled",      0),
    ("grace_ke",   "Advanced Coffee Cultivation & Roasting",      "in_progress",  25),
]

for (user_key, program_title, status, progress) in ENROLLMENTS:
    user    = created_users.get(user_key)
    program = created_programs.get(program_title)
    if user and program:
        obj, created = Enrollment.objects.get_or_create(
            user=user, program=program,
            defaults={
                "status":             status,
                "progress_percent":   progress,
                "certificate_issued": status == "certified",
                "certificate_paid":   status in ("certified", "completed"),
                "completed_at":       timezone.now() if status in ("certified", "completed") else None,
            }
        )
        if created:
            ok(f"Enrollment: {user_key} → {program_title[:45]}  [{status}]")
        else:
            skip(f"Enrollment: {user_key} → {program_title[:40]}")


# ══════════════════════════════════════════════════════════════════════════════
# 12. CONTACT INQUIRIES
# ══════════════════════════════════════════════════════════════════════════════
banner("12 · CONTACT INQUIRIES")

CONTACTS = [
    # name, email, phone, country, inquiry_type, subject, message, is_read
    ("Maria Santos",    "maria@iberiaimports.es",  "+34-91-555-0100", "Spain",   "partnership",  "Partnership Inquiry — Spain",        "We are an established import/export company in Spain interested in partnering with T&TG for coffee and electronics distribution across Southern Europe.",  True),
    ("Kwame Asante",    "kwame@ashantitrade.gh",   "+233-30-555-0200","Ghana",   "partnership",  "Partnership — West Africa",           "Ashanti Trade Limited would like to explore partnering with T&TG to extend your marketplace reach into West Africa, starting with Ghana and Ivory Coast.", False),
    ("Liu Wei",         "liu@chinaimports.cn",     "+86-10-5555-0300","China",   "investment",   "Investment Opportunity",              "Representing a consortium of investors interested in exploring investment opportunities with T&TG Trade Corporation in the Asian markets.",             False),
    ("Anna Kowalski",   "anna@poland.trade.pl",   "+48-22-555-0400","Poland",   "support",      "Technical Support — Login Issue",    "I am unable to log into my account after registering. Please assist urgently as I have pending orders on the platform.",                            True),
    ("Michael Okafor",  "m.okafor@nigeriatrade.ng","+234-1-555-0500","Nigeria", "partnership",  "Partnership — Nigeria",               "We operate a logistics and trading company in Lagos and would like to discuss becoming an official partner company for the West African region.",       False),
    ("Sophie Leblanc",  "sophie@montreal.ca",      "+1-514-555-0600","Canada",  "general",      "Avon Points — Withdrawal Query",      "I have accumulated over 5,000 Avon Points and would like to understand the withdrawal process and timeline for Q2 sell orders.",                      True),
    ("Hiroshi Yamamoto","hiroshi@japantrade.jp",   "+81-3-5555-0700","Japan",   "partnership",  "Japan Operations Expansion",          "We are a registered trading company in Tokyo and wish to become a T&TG partner for the Japanese market. Please share your partnership criteria.",      False),
]

for (name, email, phone, country, inquiry_type, subject, message, is_read) in CONTACTS:
    if not ContactInquiry.objects.filter(email=email).exists():
        ContactInquiry.objects.create(
            name=name, email=email, phone=phone, country=country,
            inquiry_type=inquiry_type, subject=subject, message=message, is_read=is_read
        )
        ok(f"Inquiry: {name}  [{inquiry_type}]  from {country}")
    else:
        skip(f"Inquiry: {email}")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
banner("SEED COMPLETE — DATABASE SUMMARY")
print(f"  Users              : {CustomUser.objects.count():>5}")
print(f"  Forex Rates        : {ForexRate.objects.count():>5}")
print(f"  Products           : {Product.objects.count():>5}")
print(f"  Orders             : {Order.objects.count():>5}")
print(f"  Product Reviews    : {ProductReview.objects.count():>5}")
print(f"  Avon Transactions  : {AvonPointTransaction.objects.count():>5}")
print(f"  Insurance Policies : {InsurancePolicy.objects.count():>5}")
print(f"  Brokerage Accounts : {BrokerageAccount.objects.count():>5}")
print(f"  Training Programs  : {TrainingProgram.objects.count():>5}")
print(f"  TV Programs        : {TVProgram.objects.count():>5}")
print(f"  Enrollments        : {Enrollment.objects.count():>5}")
print(f"  Contact Inquiries  : {ContactInquiry.objects.count():>5}")
print()
print("  Admin login → http://127.0.0.1:8000/admin/")
print("  Username: admin   Password: admin123")
print()
