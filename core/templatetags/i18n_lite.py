from django import template
from core.translations import get_text

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    """Usage: {% t "hero_title_1" %} — looks up the key in the current session language."""
    request = context.get('request')
    lang = request.session.get('lang', 'en') if request else 'en'
    return get_text(key, lang)
