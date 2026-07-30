from django.db import migrations

PROGRAMS = [
    dict(title='T&TG Coffee: From Uganda Farm to Your Cup',
         description='Follow the journey of T&TG Arabica and Robusta green coffee from Uganda farms to buyers in Canada, USA and beyond. Sourcing, processing and quality control.',
         video_url='https://www.youtube.com/embed/klmkVOCBZnI',

         thumbnail_url='https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=340&fit=crop', category='trade', is_active=True),
    dict(title='How to Use the T&TG Shopping Platform',
         description='Full walkthrough: browse products, add to cart, place orders, track shipments and earn loyalty points on the T&TG Shopping Platform.',
         video_url='https://www.youtube.com/embed/TxBRbMDKIgA',

         thumbnail_url='https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=340&fit=crop', category='ecommerce', is_active=True),
    dict(title='T&TG Loyalty Programme — Earn, Refer & Withdraw',
         description='Maximise T&TG Loyalty Points. Earn 0.5% on purchases, 1% on referrals, withdraw on Day 45. Multi-currency wallet integration explained.',
         video_url='https://www.youtube.com/embed/TxBRbMDKIgA',

         thumbnail_url='https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&h=340&fit=crop', category='ecommerce', is_active=True),
    dict(title='Forex Basics — CAD, USD, UGX, KES, EUR & JPY',
         description='How foreign exchange rates affect T&TG transactions. CAD/UGX, USD/KES, EUR/JPY explained. Bank of Canada rate references for CRA accounting.',
         video_url='https://www.youtube.com/embed/TxBRbMDKIgA',

         category='trade', is_active=True),
    dict(title='Import & Export Documentation Guide',
         description='Phytosanitary Certificates, Bills of Lading, Certificate of Origin, CBSA and CFIA compliance for coffee imports into Canada.',
         video_url='https://www.youtube.com/embed/TxBRbMDKIgA',

         category='trade', is_active=True),
]

def add_programs(apps, schema_editor):
    TVProgram = apps.get_model('training', 'TVProgram')
    for d in PROGRAMS:
        if not TVProgram.objects.filter(title=d['title']).exists():
            TVProgram.objects.create(**d)

class Migration(migrations.Migration):
    dependencies = [('training', '0006_add_thumbnail_url_to_tvprogram')]
    operations   = [migrations.RunPython(add_programs, migrations.RunPython.noop)]
