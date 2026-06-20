"""
Lightweight English/Swahili translation layer.

This is NOT Django's full i18n framework (that requires LocaleMiddleware +
LANGUAGES + LOCALE_PATHS in settings.py, which we're avoiding touching
blind since this project has other local customisations we can't see).

Instead: a simple session-based language toggle backed by a plain Python
dictionary. Currently covers the navbar, hero, and footer — the highest-
visibility, most-translated-first areas of the site. Expandable by adding
more keys to TRANSLATIONS and wrapping more template strings with the
`t` template tag (see core/templatetags/i18n_lite.py).

To expand coverage: add new key/value pairs below, then use
{% t "your_key" %} in templates instead of hardcoded text.
"""

TRANSLATIONS = {
    'en': {
        # Navbar
        'nav_home': 'Home',
        'nav_shop': 'Shop',
        'nav_trade': 'Trade & e-Commerce',
        'nav_loyalty': 'Loyalty',
        'nav_training': 'Training & TV',
        'nav_about': 'About',
        'nav_contact': 'Contact',
        'nav_signin': 'Sign In',
        'nav_getstarted': 'Get Started',

        # Hero
        'hero_eyebrow': 'Import & Export (RM) Registered',
        'hero_title_1': 'Trade &',
        'hero_title_2': 'e-Commerce',
        'hero_title_3': 'Platform',
        'hero_sub': 'T&TG Trade Corporation connects Canada, Uganda and Kenya through seamless commerce. Shop textiles, shoes, watches and coffee. Earn T&TG Loyalty Points on every purchase.',
        'hero_shop_now': 'Shop Now',
        'hero_get_started': 'Get Started Free',
        'hero_stat_products': 'Products',
        'hero_stat_countries': 'Countries',
        'hero_stat_partners': 'Partners',
        'hero_stat_orders': 'Orders',

        # Footer
        'footer_tagline': 'Connect · Trade · Grow · Earn',
        'footer_quicklinks': 'Quick Links',
        'footer_contact': 'Contact Us',
        'footer_rights': 'All rights reserved.',
    },
    'sw': {
        # Navbar
        'nav_home': 'Nyumbani',
        'nav_shop': 'Duka',
        'nav_trade': 'Biashara na Soko Mtandaoni',
        'nav_loyalty': 'Uaminifu',
        'nav_training': 'Mafunzo na TV',
        'nav_about': 'Kuhusu Sisi',
        'nav_contact': 'Wasiliana Nasi',
        'nav_signin': 'Ingia',
        'nav_getstarted': 'Anza Sasa',

        # Hero
        'hero_eyebrow': 'Imesajiliwa Uagizaji na Usafirishaji (RM)',
        'hero_title_1': 'Biashara na',
        'hero_title_2': 'Soko Mtandaoni',
        'hero_title_3': 'Jukwaa',
        'hero_sub': 'T&TG Trade Corporation inaunganisha Canada, Uganda na Kenya kupitia biashara rahisi. Nunua nguo, viatu, saa na kahawa. Pata Pointi za Uaminifu za T&TG kwa kila ununuzi.',
        'hero_shop_now': 'Nunua Sasa',
        'hero_get_started': 'Anza Bure',
        'hero_stat_products': 'Bidhaa',
        'hero_stat_countries': 'Nchi',
        'hero_stat_partners': 'Washirika',
        'hero_stat_orders': 'Maagizo',

        # Footer
        'footer_tagline': 'Unganisha · Fanya Biashara · Kua · Pata',
        'footer_quicklinks': 'Viungo vya Haraka',
        'footer_contact': 'Wasiliana Nasi',
        'footer_rights': 'Haki zote zimehifadhiwa.',
    },
}


def get_text(key, lang='en'):
    """Returns the translated string for `key` in `lang`, falling back to English, then the key itself."""
    return TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS['en'].get(key) or key
