"""
Custom template tags for robust image display.
Works with both local filesystem and Cloudinary storage.

Usage in templates:
  {% load image_tags %}
  {% product_image product.image alt="Product name" css="w-100" %}
  {% avatar_image user.profile_photo initial="T" size=44 %}
"""
from django import template
from django.conf import settings
from django.utils.html import format_html, escape

register = template.Library()


def _get_image_url(image_field):
    """
    Safely get a URL from an ImageField.
    Works with local FileSystemStorage and Cloudinary.
    Returns empty string if no image.
    """
    if not image_field:
        return ''
    try:
        url = image_field.url
        # Cloudinary sometimes returns relative URLs — ensure absolute
        if url and not url.startswith('http') and settings.USE_CLOUDINARY:
            cloud = settings.CLOUDINARY_CLOUD_NAME
            url = f'https://res.cloudinary.com/{cloud}/image/upload/{url}'
        return url
    except Exception:
        return ''


@register.simple_tag
def product_image(image_field, alt='Product', css='', category=''):
    """
    Render a product image or a category-appropriate placeholder emoji.
    """
    url = _get_image_url(image_field)
    EMOJI = {
        'electronics': '💻', 'coffee': '☕', 'pharmaceuticals': '💊',
        'agriculture': '🌾', 'textiles': '🧵', 'machinery': '⚙️',
    }
    emoji = EMOJI.get(category, '📦')

    if url:
        return format_html(
            '<img src="{}" alt="{}" class="{}" '
            'style="width:100%;height:100%;object-fit:cover" '
            'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">',
            url, escape(alt), css
        )
    else:
        return format_html(
            '<div class="product-placeholder">{}</div>',
            emoji
        )


@register.simple_tag
def avatar_image(image_field, initial='?', size=44, border=True):
    """
    Render a circular avatar image or gold initial fallback.
    """
    url = _get_image_url(image_field)
    border_style = 'border:2px solid var(--gold);' if border else ''
    base_style = (
        f'width:{size}px;height:{size}px;border-radius:50%;'
        f'object-fit:cover;flex-shrink:0;{border_style}'
    )
    fallback_style = (
        f'width:{size}px;height:{size}px;border-radius:50%;'
        'background:linear-gradient(135deg,var(--gold),var(--gold-light));'
        'display:flex;align-items:center;justify-content:center;'
        f'font-weight:800;font-size:{max(10, size//3)}px;color:var(--primary);flex-shrink:0;'
    )

    if url:
        return format_html(
            '<img src="{}" style="{}" '
            'onerror="this.outerHTML=\'<div style=\\"{}\\">{}</div>\'">',
            url, base_style, fallback_style, escape(initial.upper())
        )
    else:
        return format_html(
            '<div style="{}">{}</div>',
            fallback_style, escape(initial.upper())
        )
