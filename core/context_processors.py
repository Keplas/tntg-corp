
def cloudinary_status(request):
    from django.conf import settings
    return {
        'USE_CLOUDINARY': getattr(settings, 'USE_CLOUDINARY', False),
        'MEDIA_URL': settings.MEDIA_URL,
    }
