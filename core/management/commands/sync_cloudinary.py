"""
python manage.py sync_cloudinary --folder /path/to/images

Uploads a folder of images to Cloudinary and auto-matches them to products.

Naming rules (filename → matched to product):
  product_1.jpg        → Product with pk=1
  product_12.jpg       → Product with pk=12
  apple_macbook.jpg    → Product whose name contains 'apple macbook'
  coffee_beans.jpg     → Product whose name contains 'coffee beans'
  samsung_tv.jpg       → Product whose name contains 'samsung tv'

Underscores in filenames are treated as spaces for name matching.
"""
import os, cloudinary, cloudinary.uploader, cloudinary.api
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from marketplace.models import Product

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}


class Command(BaseCommand):
    help = 'Upload images from a local folder to Cloudinary and link to products'

    def add_arguments(self, parser):
        parser.add_argument('--folder',  type=str, help='Path to local image folder')
        parser.add_argument('--dry-run', action='store_true', help='Show matches without uploading')
        parser.add_argument('--list',    action='store_true', help='List all products with their IDs')

    def handle(self, *args, **options):
        # ── Check Cloudinary ──────────────────────────────────────────────
        if not getattr(settings, 'USE_CLOUDINARY', False):
            raise CommandError(
                'Cloudinary is not configured.\n'
                'Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, '
                'CLOUDINARY_API_SECRET environment variables first.'
            )

        cloudinary.config(
            cloud_name = settings.CLOUDINARY_CLOUD_NAME,
            api_key    = settings.CLOUDINARY_API_KEY,
            api_secret = settings.CLOUDINARY_API_SECRET,
            secure     = True,
        )

        # ── List mode ─────────────────────────────────────────────────────
        if options['list']:
            self.stdout.write('\n📦  All Products:\n')
            self.stdout.write(f'  {"ID":<6} {"Category":<15} {"Name"}\n')
            self.stdout.write(f'  {"─"*6} {"─"*15} {"─"*40}\n')
            for p in Product.objects.order_by('id'):
                img = '✓' if p.image else '✗'
                self.stdout.write(
                    f'  {p.pk:<6} {p.get_category_display():<15} '
                    f'[{img}] {p.name}'
                )
            self.stdout.write('\n  ✓ = has image  ✗ = no image\n')
            return

        # ── Require --folder ──────────────────────────────────────────────
        folder = options.get('folder')
        if not folder:
            raise CommandError('Provide --folder /path/to/images  or --list')

        if not os.path.isdir(folder):
            raise CommandError(f'Folder not found: {folder}')

        # ── Gather image files ─────────────────────────────────────────────
        files = [
            f for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in SUPPORTED
        ]
        if not files:
            raise CommandError(f'No supported images found in {folder}')

        self.stdout.write(f'\n🖼️  Found {len(files)} image(s) in {folder}\n')

        products = list(Product.objects.all())
        uploaded = 0
        skipped  = 0
        no_match = []

        for filename in sorted(files):
            stem, ext = os.path.splitext(filename)
            filepath   = os.path.join(folder, filename)
            product    = None

            # ── Match by product_<id> pattern ─────────────────────────────
            if stem.lower().startswith('product_'):
                try:
                    pk = int(stem.split('_', 1)[1])
                    product = Product.objects.get(pk=pk)
                except (ValueError, Product.DoesNotExist):
                    pass

            # ── Match by name (underscores → spaces) ──────────────────────
            if not product:
                search_term = stem.replace('_', ' ').lower()
                for p in products:
                    if search_term in p.name.lower() or p.name.lower() in search_term:
                        product = p
                        break

            if not product:
                no_match.append(filename)
                self.stderr.write(f'  ✗  No match: {filename}')
                continue

            self.stdout.write(
                f'  {"[DRY]" if options["dry_run"] else "↑"} '
                f'{filename}  →  [{product.pk}] {product.name}'
            )

            if not options['dry_run']:
                try:
                    result = cloudinary.uploader.upload(
                        filepath,
                        folder      = 'tntg/products',
                        public_id   = f'product_{product.pk}',
                        overwrite   = True,
                        resource_type = 'image',
                        transformation = [{'quality': 'auto', 'fetch_format': 'auto'}],
                    )
                    # Save the Cloudinary public_id as the image field value
                    product.image = result['public_id']
                    product.save(update_fields=['image'])
                    self.stdout.write(f'     ✅  URL: {result["secure_url"]}')
                    uploaded += 1
                except Exception as e:
                    self.stderr.write(f'     ❌  Upload failed: {e}')
            else:
                uploaded += 1

        # ── Summary ───────────────────────────────────────────────────────
        action = 'Would upload' if options['dry_run'] else 'Uploaded'
        self.stdout.write(f'\n{"─"*50}')
        self.stdout.write(f'  {action}: {uploaded}')
        if no_match:
            self.stdout.write(f'  No match:  {len(no_match)}')
            self.stdout.write('  Unmatched files:')
            for f in no_match:
                self.stdout.write(f'    • {f}')
            self.stdout.write(
                '\n  Tip: Rename files as  product_<ID>.jpg  to force a match.'
                '\n  Run  python manage.py sync_cloudinary --list  to see all IDs.'
            )
