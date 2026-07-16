from django.db import migrations

IRRELEVANT = [
    'Modern & Tech Farming', 'Corporate Mid-Market',
    'Financial Services', 'Aquaponics',
    'Insurance', 'Investment Portfolio', 'Real Estate'
]

def deactivate(apps, schema_editor):
    try:
        TrainingProgram = apps.get_model('training', 'TrainingProgram')
        for keyword in IRRELEVANT:
            qs = TrainingProgram.objects.filter(title__icontains=keyword)
            if hasattr(TrainingProgram._meta.get_field('title'), 'is_active'):
                qs.update(is_active=False)
    except Exception:
        pass  # Training model may not have is_active field — skip

class Migration(migrations.Migration):
    dependencies = [('core', '0005_add_newsletter_subscriber')]
    operations   = [migrations.RunPython(deactivate, migrations.RunPython.noop)]
