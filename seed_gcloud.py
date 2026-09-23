"""
T&TG Trade Corp — Google Cloud database seeder
Creates all initial products, blog posts and training events
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings_gcloud')
django.setup()

from marketplace.models import Product
from core.models import BlogPost
from training.models import TrainingEvent, TrainingProgram
from accounts.models import CustomUser

print("=== Seeding T&TG Database ===")

# ── Superuser ──────────────────────────────────────────────────────────────────
if not CustomUser.objects.filter(username='tom').exists():
    CustomUser.objects.create_superuser(
        username='tom',
        email='tom.grouptrade@gmail.com',
        password='Tomssembiito12#',
        first_name='Tom',
        last_name='Ssembiito',
    )
    print("Superuser created: tom / Tomssembiito12#")
else:
    print("Superuser already exists")

seller = CustomUser.objects.get(username='tom')

# ── Products ──────────────────────────────────────────────────────────────────
products = [
    {'name':'T&TG Arabica Green Coffee','price':35.00,'category':'coffee','market_type':'both','description':'Premium Uganda Arabica green coffee beans. Single origin, traceable from farm to cup.','image_url':'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=400&fit=crop','is_featured':True},
    {'name':'T&TG Robusta Green Coffee','price':28.00,'category':'coffee','market_type':'both','description':'Bold Uganda Robusta green coffee. High caffeine, full body, ideal for espresso blends.','image_url':'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&h=400&fit=crop','is_featured':True},
    {'name':'T&TG Instant Coffee Medium Roast','price':12.99,'category':'coffee','market_type':'consumer','description':'Smooth and aromatic instant coffee. Ready in seconds, crafted from Uganda Arabica beans.','image_url':'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&h=400&fit=crop'},
    {'name':'Belfour Coffee Bar Soap 150g','price':8.99,'category':'coffee','market_type':'consumer','description':'Artisanal coffee soap made with real Uganda coffee grounds. Exfoliating and energising.','image_url':'https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=600&h=400&fit=crop'},
    {'name':'T&TG Artisanal Coffee Swirl Soap','price':9.99,'category':'coffee','market_type':'consumer','description':'Handcrafted coffee swirl soap with shea butter. Natural and skin-nourishing.','image_url':'https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=600&h=400&fit=crop'},
    {'name':'T&TG Coffee and Clove Soap','price':9.99,'category':'coffee','market_type':'consumer','description':'Coffee and clove artisanal soap with cinnamon ground coffee. Warming and invigorating.','image_url':'https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=600&h=400&fit=crop'},
    {'name':'T&TG Rustic Coffee Invitation Set','price':48.00,'category':'merchandise','market_type':'consumer','description':'Kraft paper invitation set with coffee wax seal. Perfect for coffee-themed events and gifting.','image_url':'/static/images/product_invitation_rustic.jpg'},
    {'name':"T&TG 'The Perfect Blend' Gift Set",'price':62.00,'category':'merchandise','market_type':'consumer','description':'Premium coffee wedding and gifting stationery set. Elegant kraft paper design.','image_url':'/static/images/product_invitation_blend.jpg'},
    {'name':'T&TG Artisanal Luxury Coffee Pen','price':38.00,'category':'merchandise','market_type':'consumer','description':'Black and gold luxury pen. The perfect gift for coffee lovers and business partners.','image_url':'/static/images/product_pen_luxury.jpg'},
    {'name':'T&TG Coffee Notebook and Pen Set','price':35.00,'category':'merchandise','market_type':'consumer','description':'Dark coffee-themed notebook with matching pen. Ideal for meetings, notes and gifting.','image_url':'/static/images/product_notebook_coffee.jpg'},
    {'name':'T&TG Handcrafted Wooden Fountain Pen','price':55.00,'category':'merchandise','market_type':'consumer','description':'Artisan wooden fountain pen. Handcrafted and unique. A premium business gift.','image_url':'/static/images/product_pen_wooden.jpg'},
]

for p in products:
    obj, created = Product.objects.get_or_create(
        name=p['name'],
        defaults={**p, 'seller': seller, 'is_active': True, 'stock': 100}
    )
    print(f"{'Created' if created else 'Exists'}: {obj.name}")

# ── Blog Posts ────────────────────────────────────────────────────────────────
posts = [
    {
        'title': 'T&TG Trade Corporation: Connecting Uganda Coffee to the World',
        'slug': 'tntg-connecting-uganda-coffee-world',
        'category': 'trade',
        'excerpt': 'T&TG Trade Corp connects Uganda premium Arabica and Robusta coffee to Canada, USA, Netherlands and Japan.',
        'content': 'T&TG Trade Corporation was founded on August 26, 2026 with a clear mission: to connect premium Ugandan and Kenyan coffee to global buyers through transparent, traceable and fair trade. Operating across six countries including Canada, USA, Uganda, Kenya, Netherlands and Japan, T&TG provides a fully integrated trade and e-Commerce platform for coffee suppliers, distributors and regional managers worldwide.',
        'cover_image_url': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1200&h=600&fit=crop',
        'is_published': True, 'is_featured': True,
    },
    {
        'title': 'How T&TG Loyalty Points Work: Earn 0.5% on Every Purchase',
        'slug': 'how-tntg-loyalty-points-work',
        'category': 'loyalty',
        'excerpt': 'Learn how T&TG Loyalty Points work and earn 0.5% on every purchase, 1% on every referral, with payouts on Day 45.',
        'content': 'T&TG Loyalty Points reward every customer who shops on the T&TG platform. Earn 0.5% of your purchase value as loyalty points on every order. Refer a friend and earn 1% of their first purchase. Points accumulate in your wallet and are paid out on Day 45. The T&TG Loyalty Programme has four pillars: Points, Promotions, Referral and Reward.',
        'cover_image_url': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&h=600&fit=crop',
        'is_published': True,
    },
    {
        'title': 'Understanding Live Forex Rates at T&TG: CAD, USD, UGX, KES, EUR and JPY',
        'slug': 'understanding-live-forex-rates-tntg',
        'category': 'forex',
        'excerpt': 'T&TG provides live CAD/UGX, CAD/KES, EUR/CAD and JPY/CAD forex rates for all six operating countries.',
        'content': 'T&TG Trade Corporation displays live exchange rates for all six operating countries. Our forex system covers CAD to UGX, CAD to KES, USD to UGX, EUR to UGX and JPY to UGX. Rates are updated every hour from the European Central Bank via the Frankfurter API. All prices on the T&TG shopping platform can be displayed in your local currency.',
        'cover_image_url': '/static/images/forex_chart.png',
        'is_published': True,
    },
    {
        'title': 'Partner With T&TG: Coffee Suppliers, Distributors and Regional Managers',
        'slug': 'partner-with-tntg-coffee-suppliers',
        'category': 'trade',
        'excerpt': 'T&TG welcomes coffee suppliers in Uganda and Kenya, distributors in Canada, USA, Netherlands and Japan, and regional managers worldwide.',
        'content': 'T&TG Trade Corporation is actively seeking coffee suppliers, distributors and regional managers across all six operating countries. Coffee farmers and cooperatives in Uganda and Kenya can register their farms and enter direct purchase agreements with T&TG. Distributors and roasters in Canada, USA, Netherlands and Japan can access consistent supply of premium Arabica and Robusta green coffee. Regional managers earn commission on all referred sales.',
        'cover_image_url': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200&h=600&fit=crop',
        'is_published': True,
    },
]

for p in posts:
    obj, created = BlogPost.objects.get_or_create(
        slug=p['slug'],
        defaults={**p, 'author': seller}
    )
    print(f"{'Created' if created else 'Exists'}: {obj.title[:50]}")

# ── Training Events ────────────────────────────────────────────────────────────
from django.utils import timezone
from datetime import timedelta

events = [
    {'title':'How to Use the T&TG Shopping Platform','description':'Learn how to browse, order and track coffee products on the T&TG platform.','thumbnail_url':'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=340&fit=crop','capacity':50,'event_date':timezone.now()+timedelta(days=7)},
    {'title':'T&TG Loyalty Points and Referral Programme','description':'A complete guide to earning and redeeming T&TG Loyalty Points and referring new members.','thumbnail_url':'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&h=340&fit=crop','capacity':50,'event_date':timezone.now()+timedelta(days=14)},
    {'title':'Import and Export Operations with T&TG','description':'Learn how T&TG manages coffee imports and exports across Canada, Uganda, Kenya, Netherlands and Japan.','thumbnail_url':'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=600&h=340&fit=crop','capacity':30,'event_date':timezone.now()+timedelta(days=21)},
    {'title':'Live Forex Rates: CAD, USD, UGX, KES, EUR and JPY','description':'Understand how T&TG uses live forex rates for cross-border pricing and trade.','thumbnail_url':'/static/images/forex_chart.png','capacity':50,'event_date':timezone.now()+timedelta(days=28)},
]

for e in events:
    obj, created = TrainingEvent.objects.get_or_create(
        title=e['title'],
        defaults={**e, 'is_active': True, 'price': 0.00}
    )
    print(f"{'Created' if created else 'Exists'}: {obj.title[:50]}")

print("\n=== Seeding Complete ===")
print(f"Products: {Product.objects.count()}")
print(f"Blog posts: {BlogPost.objects.count()}")
print(f"Training events: {TrainingEvent.objects.count()}")
print(f"Users: {CustomUser.objects.count()}")
