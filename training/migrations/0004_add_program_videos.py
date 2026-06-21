from django.db import migrations

TRADE_TITLE     = 'Import & Export Operations'
ECOMMERCE_TITLE = 'E-Commerce Business Setup & Management'

TRADE_VIDEO_URL     = 'https://www.youtube.com/watch?v=wKJL1zO8ZTc'   # How to Start an Import Export Business from Home — Step-by-Step Guide
ECOMMERCE_VIDEO_URL = 'https://www.youtube.com/watch?v=4pWi9N5Obzs'   # How to Start an Ecommerce Business — A Complete Blueprint (Learn With Shopify)

TV_PROGRAMS = [
    dict(title='Import & Export Operations — Getting Started',
         description='A step-by-step walkthrough of starting an import & export business: sourcing products, customs documentation, shipping logistics, and finding your first buyers and suppliers.',
         video_url=TRADE_VIDEO_URL,
         broadcast_schedule='Available anytime — on demand',
         category='Import & Export', is_live=False, is_active=True),

    dict(title='E-Commerce Business Setup — Getting Started',
         description='A complete blueprint for setting up an online store: choosing a niche, building your storefront, payments, and your first marketing steps.',
         video_url=ECOMMERCE_VIDEO_URL,
         broadcast_schedule='Available anytime — on demand',
         category='E-Commerce', is_live=False, is_active=True),
]


def add_program_videos(apps, schema_editor):
    TrainingProgram = apps.get_model('training', 'TrainingProgram')
    TVProgram = apps.get_model('training', 'TVProgram')

    TrainingProgram.objects.filter(title=TRADE_TITLE).update(video_url=TRADE_VIDEO_URL)
    TrainingProgram.objects.filter(title=ECOMMERCE_TITLE).update(video_url=ECOMMERCE_VIDEO_URL)

    for data in TV_PROGRAMS:
        title = data['title']
        existing = TVProgram.objects.filter(title=title).first()
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            existing.save()
        else:
            TVProgram.objects.create(**data)


def reverse_add_program_videos(apps, schema_editor):
    TrainingProgram = apps.get_model('training', 'TrainingProgram')
    TVProgram = apps.get_model('training', 'TVProgram')

    TrainingProgram.objects.filter(title__in=[TRADE_TITLE, ECOMMERCE_TITLE]).update(video_url='')
    TVProgram.objects.filter(title__in=[p['title'] for p in TV_PROGRAMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_update_training_programs'),
    ]

    operations = [
        migrations.RunPython(add_program_videos, reverse_add_program_videos),
    ]
