"""python manage.py check_cloudinary — verifies Cloudinary connection"""
import cloudinary, cloudinary.api
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Cloudinary connection'

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_CLOUDINARY', False):
            self.stderr.write(
                '❌  Cloudinary is NOT configured.\n'
                '    Set these environment variables:\n'
                '      CLOUDINARY_CLOUD_NAME\n'
                '      CLOUDINARY_API_KEY\n'
                '      CLOUDINARY_API_SECRET\n'
            )
            return

        try:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
            )
            result = cloudinary.api.ping()
            self.stdout.write(
                f'✅  Cloudinary connected!\n'
                f'    Cloud: {settings.CLOUDINARY_CLOUD_NAME}\n'
                f'    Status: {result.get("status", "ok")}\n'
                f'    Storage: {settings.DEFAULT_FILE_STORAGE}\n'
            )
        except Exception as e:
            self.stderr.write(f'❌  Connection failed: {e}')
