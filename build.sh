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


# Create merchandise products (idempotent — skips if already exist)
python manage.py shell -c "
from marketplace.models import Product
from accounts.models import CustomUser
seller = CustomUser.objects.filter(is_staff=True).first()
products = [
  dict(name='T&TG Rustic Coffee Invitation Set', category='coffee', price='48.00', currency='CAD', unit='set', quantity_available=50, market_type='both', origin_country='Canada', is_active=True, is_featured=True, description='Rustic coffee-themed invitation set. 10 cards on premium kraft paper with wax seal and dried flower accent.'),
  dict(name='T&TG Perfect Blend Gift Set', category='coffee', price='62.00', currency='CAD', unit='set', quantity_available=40, market_type='both', origin_country='Canada', is_active=True, is_featured=True, description='Coffee-themed gift stationery — The Perfect Blend. 10 kraft paper cards with coffee cup tag and jute twine.'),
  dict(name='T&TG Artisanal Luxury Coffee Pen', category='coffee', price='38.00', currency='CAD', unit='piece', quantity_available=100, market_type='both', origin_country='Canada', is_active=True, is_featured=False, description='Premium handcrafted luxury ballpoint pen with black and gold coffee-pattern design. Elegant corporate gift.'),
  dict(name='T&TG Coffee Notebook and Pen Set', category='coffee', price='35.00', currency='CAD', unit='set', quantity_available=75, market_type='both', origin_country='Canada', is_active=True, is_featured=False, description='Premium dark coffee-brown spiral notebook with matching pen. 200 pages A5 lay-flat. Ideal for trade meetings.'),
  dict(name='T&TG Handcrafted Wooden Fountain Pen', category='coffee', price='55.00', currency='CAD', unit='piece', quantity_available=30, market_type='both', origin_country='Canada', is_active=True, is_featured=True, description='Exquisite artisan fountain pen in dark rosewood with gold-plated nib. Distinguished gift for trade partners.'),
]
for p in products:
    obj, created = Product.objects.get_or_create(name=p['name'], defaults={**p, 'seller': seller})
    print(('Created' if created else 'Exists'), obj.name)
"

echo "Build complete ✓"
