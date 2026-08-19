from django.db import migrations

PRODUCTS = [
    dict(
        name              = "T&TG Rustic Coffee Invitation Set",
        category          = "coffee",
        description       = "A beautifully crafted rustic coffee-themed invitation set for events, launches and corporate gatherings. Includes 10 invitations on premium kraft paper with wax seal, twine and dried flower accent. Perfect for T&TG trade events and coffee launch ceremonies.",
        price             = "48.00",
        currency          = "CAD",
        unit              = "set",
        quantity_available= 50,
        market_type       = "both",
        origin_country    = "Canada",
        is_active         = True,
        is_featured       = True,
        image_url         = "https://images.unsplash.com/photo-1606216794074-735e91aa2c92?w=600&h=600&fit=crop",
    ),
    dict(
        name              = "T&TG 'The Perfect Blend' Gift Set",
        category          = "coffee",
        description       = "Premium coffee-themed gift stationery set — 'The Perfect Blend'. Includes 10 kraft paper cards with coffee cup wooden tag and jute twine ribbon. Ideal for corporate gifting, client appreciation and trade partner welcome packs.",
        price             = "62.00",
        currency          = "CAD",
        unit              = "set",
        quantity_available= 40,
        market_type       = "both",
        origin_country    = "Canada",
        is_active         = True,
        is_featured       = True,
        image_url         = "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&h=600&fit=crop",
    ),
    dict(
        name              = "T&TG Artisanal Luxury Coffee Pen",
        category          = "coffee",
        description       = "A premium handcrafted luxury ballpoint pen with black and gold coffee-pattern design. Smooth German ink refill. An elegant corporate gift for T&TG trade partners, business clients and coffee industry professionals.",
        price             = "38.00",
        currency          = "CAD",
        unit              = "piece",
        quantity_available= 100,
        market_type       = "both",
        origin_country    = "Canada",
        is_active         = True,
        is_featured       = False,
        image_url         = "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=600&h=600&fit=crop",
    ),
    dict(
        name              = "T&TG Coffee Notebook & Pen Set",
        category          = "coffee",
        description       = "A premium dark coffee-brown spiral notebook with matching pen — inspired by T&TG's coffee heritage. 200 pages, A5 size, lay-flat binding. Ideal for trade meetings, onboarding sessions and corporate gifting across all 6 T&TG markets.",
        price             = "35.00",
        currency          = "CAD",
        unit              = "set",
        quantity_available= 75,
        market_type       = "both",
        origin_country    = "Canada",
        is_active         = True,
        is_featured       = False,
        image_url         = "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=600&h=600&fit=crop",
    ),
    dict(
        name              = "T&TG Handcrafted Wooden Fountain Pen",
        category          = "coffee",
        description       = "An exquisite handcrafted artisan fountain pen made from premium dark rosewood and olive wood, fitted with a gold-plated nib. Each pen is unique — no two are the same. A distinguished gift for T&TG trade partners, directors and managing directors.",
        price             = "55.00",
        currency          = "CAD",
        unit              = "piece",
        quantity_available= 30,
        market_type       = "both",
        origin_country    = "Canada",
        is_active         = True,
        is_featured       = True,
        image_url         = "https://images.unsplash.com/photo-1585336261022-680e295ce3fe?w=600&h=600&fit=crop",
    ),
]

def add_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    User    = apps.get_model('accounts', 'CustomUser')
    seller  = User.objects.filter(is_staff=True).first()
    for d in PRODUCTS:
        if not Product.objects.filter(name=d['name']).exists():
            Product.objects.create(seller=seller, **d)

class Migration(migrations.Migration):
    dependencies = [('marketplace', '0015_add_display_currency_to_order')]
    operations   = [migrations.RunPython(add_products, migrations.RunPython.noop)]
