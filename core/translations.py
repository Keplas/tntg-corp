"""
Lightweight English/Luganda translation layer.

Session-based language toggle backed by a plain Python dictionary.
Covers the navbar, hero, and footer. Expandable by adding more keys
to TRANSLATIONS and wrapping template strings with the `t` template tag.
"""

TRANSLATIONS = {
    'en': {
        # Navbar
        'nav_home':       'Home',
        'nav_shop':       'Shop',
        'nav_trade':      'Trade & e-Commerce',
        'nav_loyalty':    'Loyalty',
        'nav_training':   'Onboarding Program',
        'nav_about':      'About',
        'nav_contact':    'Contact',
        'nav_signin':     'Sign In',
        'nav_getstarted': 'Get Started',

        # Hero
        'hero_eyebrow':        'Import & Export (RM) Registered',
        'hero_title_1':        'Trade &',
        'hero_title_2':        'e-Commerce',
        'hero_title_3':        'Platform',
        'hero_sub':            "T&TG Trade Corporation based in Toronto, ON Canada connects Uganda, Kenya and USA through seamless e-commerce. Shop T&TG's Artisanal, Arabica and Robusta Coffee. Earn T&TG Loyalty Points on every purchase.",
        'hero_shop_now':       'Shop Now',
        'hero_get_started':    'Get Started Free',
        'hero_stat_products':  'Products',
        'hero_stat_countries': 'Countries',
        'hero_stat_partners':  'Partners',
        'hero_stat_orders':    'Orders',

        # Footer
        'footer_tagline':    'Connect · Trade · Grow · Earn',
        'footer_quicklinks': 'Quick Links',
        'footer_contact':    'Contact Us',
        'footer_rights':     'All rights reserved.',
    },
    'lg': {
        # Navbar — Luganda
        'nav_home':       'Eka',
        'nav_shop':       'Sitoowa',
        'nav_trade':      'Bulungi bw\'Obusuubuzi',
        'nav_loyalty':    'Obwesigwa',
        'nav_training':   'Pulogulamu y\'Okuyigiriza',
        'nav_about':      'Ebikutuusa',
        'nav_contact':    'Tukwetaane',
        'nav_signin':     'Yingira',
        'nav_getstarted': 'Tandika Kaakano',

        # Hero — Luganda
        'hero_eyebrow':        'Eyawandiisibwa mu Kutwaala era Okulimba (RM)',
        'hero_title_1':        'Busuubuzi &',
        'hero_title_2':        'Obusuubuzi ku',
        'hero_title_3':        'Muterekero',
        'hero_sub':            'T&TG Trade Corporation efuluma mu Toronto, Canada eteekateeka Uganda, Kenya ne USA mu busuubuzi obulungi. Gula kahawa ya T&TG Artisanal, Arabica ne Robusta. Funa T&TG Loyalty Points ku buli ginawo.',
        'hero_shop_now':       'Gula Kaakano',
        'hero_get_started':    'Tandika Bwereere',
        'hero_stat_products':  'Ebintu',
        'hero_stat_countries': 'Ensi',
        'hero_stat_partners':  'Abooluganda',
        'hero_stat_orders':    'Ebirowoozo',

        # Footer — Luganda
        'footer_tagline':    'Kwatagana · Suubula · Kulungi · Funa',
        'footer_quicklinks': 'Enteekateeka Yanguwa',
        'footer_contact':    'Tukwetaane',
        'footer_rights':     'Ebisooka byonna byazikirizibwa.',
    },
}


def get_text(key, lang='en'):
    """Returns the translated string for key in lang, falling back to English."""
    return TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS['en'].get(key) or key
