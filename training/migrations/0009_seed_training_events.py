from django.db import migrations
from django.utils import timezone
from datetime import timedelta

def add_events(apps, schema_editor):
    TrainingEvent = apps.get_model('training', 'TrainingEvent')
    now = timezone.now()
    events = [
        dict(
            title="How to Use the T&TG Shopping Platform",
            category="shopping",
            description="A live walkthrough of the T&TG Shopping Platform covering product browsing, cart management, checkout, order tracking and loyalty points earned on every purchase.",
            agenda="05:00 PM – Registration\n06:00 PM – Welcome & Introduction\n06:15 PM – Live Demo: Browsing & Cart\n06:45 PM – Checkout & Order Tracking\n07:00 PM – Loyalty Points Q&A\n07:30 PM – Networking",
            event_date=now + timedelta(days=7),
            duration_mins=90,
            capacity=100,
            is_free=True,
            price_points=0,
            video_url="",
            thumbnail_url="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=340&fit=crop",
            is_active=True,
        ),
        dict(
            title="T&TG Loyalty Points & Referral Programme",
            category="loyalty",
            description="Learn how to earn 0.5% T&TG Loyalty Points on every purchase, refer friends for 1% rewards, and withdraw your points as cash on Day 45.",
            agenda="05:00 PM – Registration\n06:00 PM – How Points Are Earned\n06:30 PM – Referral System Demo\n07:00 PM – Withdrawal Process\n07:20 PM – Multi-Currency Wallet\n07:45 PM – Q&A",
            event_date=now + timedelta(days=14),
            duration_mins=105,
            capacity=100,
            is_free=True,
            price_points=0,
            video_url="",
            thumbnail_url="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&h=340&fit=crop",
            is_active=True,
        ),
        dict(
            title="Import & Export Operations with T&TG",
            category="trade",
            description="A complete guide to applying for T&TG trade partner status, understanding Incoterms, completing export documentation, and managing shipments from Uganda and Kenya to Canada, Netherlands and Japan.",
            agenda="05:00 PM – Registration\n06:00 PM – Trade Application Process\n06:30 PM – Export Documentation Guide\n07:00 PM – Incoterms & Payment Terms\n07:20 PM – Real Shipment Case Study\n07:45 PM – Q&A with Tom Ssembiito",
            event_date=now + timedelta(days=21),
            duration_mins=120,
            capacity=80,
            is_free=True,
            price_points=0,
            video_url="",
            thumbnail_url="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=600&h=340&fit=crop",
            is_active=True,
        ),
        dict(
            title="Live Forex Rates: CAD, USD, UGX, KES, EUR & JPY",
            category="forex",
            description="Understand how T&TG live exchange rates work, how to convert currencies in your multi-currency wallet, and the legal framework governing forex display under Ontario's Consumer Protection Act.",
            agenda="05:00 PM – Registration\n06:00 PM – Reading Live Forex Rates\n06:30 PM – Currency Conversion Demo\n07:00 PM – CRA & Bank of Canada Compliance\n07:30 PM – Q&A",
            event_date=now + timedelta(days=28),
            duration_mins=90,
            capacity=100,
            is_free=True,
            price_points=0,
            video_url="",
            thumbnail_url="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&h=340&fit=crop",
            is_active=True,
        ),
    ]
    for e in events:
        TrainingEvent.objects.get_or_create(title=e['title'], defaults=e)

class Migration(migrations.Migration):
    dependencies = [('training', '0008_add_training_events_tickets')]
    operations   = [migrations.RunPython(add_events, migrations.RunPython.noop)]
