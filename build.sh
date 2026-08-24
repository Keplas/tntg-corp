#!/usr/bin/env bash
# Render build script — runs on every deploy
set -o errexit

pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create superuser from environment variables (only if it doesn't exist)
python manage.py shell -c "
from accounts.models import CustomUser
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if username and password and not CustomUser.objects.filter(username=username).exists():
    CustomUser.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username!r} created.')
else:
    print('Superuser already exists or env vars not set — skipping.')
"



# Remove duplicate products (keep the ones with full descriptions)
python manage.py shell -c "
from marketplace.models import Product
short = Product.objects.filter(name='T&TG Perfect Blend Gift Set')
if short.exists(): short.delete(); print('Removed duplicate: T&TG Perfect Blend Gift Set')
short2 = Product.objects.filter(name='T&TG Coffee Notebook and Pen Set')
if short2.exists(): short2.delete(); print('Removed duplicate: T&TG Coffee Notebook and Pen Set')
" || echo 'Duplicate cleanup skipped'


# Set product images via static files
python manage.py shell -c "
from marketplace.models import Product

images = {
    'T&TG Rustic Coffee Invitation Set':      '/static/images/product_invitation_rustic.jpg',
    'T&TG Perfect Blend Gift Set':            '/static/images/product_invitation_blend.jpg',
    "T&TG 'The Perfect Blend' Gift Set":    '/static/images/product_invitation_blend.jpg',
    'T&TG Artisanal Luxury Coffee Pen':       '/static/images/product_pen_luxury.jpg',
    'T&TG Coffee Notebook and Pen Set':       '/static/images/product_notebook_coffee.jpg',
    'T&TG Coffee Notebook & Pen Set':         '/static/images/product_notebook_coffee.jpg',
    'T&TG Handcrafted Wooden Fountain Pen':   '/static/images/product_pen_wooden.jpg',
}
for name, url in images.items():
    updated = Product.objects.filter(name=name).update(image_url=url)
    if updated: print('Image set for:', name)
" || echo 'Image update skipped'

# Create merchandise products (idempotent)
python create_products.py || echo "Product creation skipped"

echo "Build complete ✓"
