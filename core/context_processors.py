
def cloudinary_status(request):
    from django.conf import settings
    return {
        'USE_CLOUDINARY': getattr(settings, 'USE_CLOUDINARY', False),
        'MEDIA_URL': settings.MEDIA_URL,
    }


def social_links(request):
    from django.conf import settings
    return {
        'SOCIAL_LINKEDIN':  getattr(settings, 'SOCIAL_LINKEDIN',  ''),
        'SOCIAL_FACEBOOK':  getattr(settings, 'SOCIAL_FACEBOOK',  ''),
        'SOCIAL_INSTAGRAM': getattr(settings, 'SOCIAL_INSTAGRAM', ''),
        'SOCIAL_TIKTOK':    getattr(settings, 'SOCIAL_TIKTOK',    ''),
        'SOCIAL_WHATSAPP':  getattr(settings, 'SOCIAL_WHATSAPP',  'https://wa.me/14168323512'),
    }
