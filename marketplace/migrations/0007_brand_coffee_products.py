from django.db import migrations

# The branded T&TG Coffee package photo replaces the generic Unsplash stock
# photo for both coffee products. Shipped as a static asset (not an upload)
# so it survives Render deploys without needing Cloudinary configured.
BRANDED_COFFEE_IMAGE_URL = 'https://tntgcorp.com/static/images/products/tg-coffee-bag.jpg'

COFFEE_PRODUCT_NAMES = ['Arabica Green Coffee', 'Robusta Green Coffee']


def brand_coffee_products(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    Product.objects.filter(name__in=COFFEE_PRODUCT_NAMES).update(image_url=BRANDED_COFFEE_IMAGE_URL)


def reverse_brand_coffee_products(apps, schema_editor):
    # Not meaningfully reversible (previous stock-photo URLs aren't stored
    # anywhere to restore) — no-op on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_alter_product_gender_target'),
    ]

    operations = [
        migrations.RunPython(brand_coffee_products, reverse_brand_coffee_products),
    ]
