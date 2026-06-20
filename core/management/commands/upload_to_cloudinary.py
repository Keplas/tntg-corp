"""
Management command: python manage.py upload_to_cloudinary

Uploads any locally stored product/profile images to Cloudinary
and updates the database records to point to the new Cloudinary URLs.
Run this ONCE after setting your Cloudinary credentials.
"""
import os
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.conf import settings
from marketplace.models import Product
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Upload existing local media files to Cloudinary'

    def handle(self, *args, **options):
        cloud = settings.CLOUDINARY_STORAGE
        if not cloud.get('CLOUD_NAME'):
            self.stderr.write('❌  CLOUDINARY_CLOUD_NAME not set. Add environment variables first.')
            return

        cloudinary.config(
            cloud_name=cloud['CLOUD_NAME'],
            api_key=cloud['API_KEY'],
            api_secret=cloud['API_SECRET'],
        )
        self.stdout.write('☁️  Connected to Cloudinary\n')

        uploaded = 0
        skipped  = 0

        # ── Product images ─────────────────────────────────────────────────
        self.stdout.write('📦  Scanning products...')
        for product in Product.objects.exclude(image='').exclude(image=None):
            local_path = os.path.join(settings.BASE_DIR, 'media', str(product.image))
            if os.path.exists(local_path):
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder='tntg/products',
                        public_id=f'product_{product.pk}',
                        overwrite=True,
                        resource_type='image',
                    )
                    product.image = result['public_id']
                    product.save(update_fields=['image'])
                    self.stdout.write(f'  ✓ Product #{product.pk}: {product.name}')
                    uploaded += 1
                except Exception as e:
                    self.stderr.write(f'  ✗ Product #{product.pk}: {e}')
            else:
                skipped += 1

        # ── User profile photos ────────────────────────────────────────────
        self.stdout.write('\n👤  Scanning user profiles...')
        for user in CustomUser.objects.exclude(profile_photo='').exclude(profile_photo=None):
            local_path = os.path.join(settings.BASE_DIR, 'media', str(user.profile_photo))
            if os.path.exists(local_path):
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder='tntg/profiles',
                        public_id=f'profile_{user.pk}',
                        overwrite=True,
                        resource_type='image',
                    )
                    user.profile_photo = result['public_id']
                    user.save(update_fields=['profile_photo'])
                    self.stdout.write(f'  ✓ User: {user.username}')
                    uploaded += 1
                except Exception as e:
                    self.stderr.write(f'  ✗ User {user.username}: {e}')
            else:
                skipped += 1

        self.stdout.write(f'\n✅  Done — {uploaded} uploaded, {skipped} skipped (no local file).')
# — end of existing command —
