from django.db import migrations

FINAL_TRADE_TITLE     = 'Import & Export Operations'
FINAL_ECOMMERCE_TITLE = 'E-Commerce Business Setup & Management'

# Known title variations seen across different seed/test runs of this project —
# consolidated into the two final titles above rather than left as duplicates.
TRADE_VARIANTS     = ['Import & Export Operations', 'Import/Export Operations']
ECOMMERCE_VARIANTS = ['E-Commerce Business Setup & Management', 'Trade & e-Commerce Business Setup']


def update_training_programs(apps, schema_editor):
    TrainingProgram = apps.get_model('training', 'TrainingProgram')

    # Consolidate any "import/export"-style duplicates into one active program
    # with the final title; deactivate the rest rather than deleting (in case
    # any have existing enrollments tied to them).
    trade_qs = TrainingProgram.objects.filter(title__in=TRADE_VARIANTS)
    if trade_qs.exists():
        keeper = trade_qs.filter(title=FINAL_TRADE_TITLE).first() or trade_qs.first()
        keeper.title = FINAL_TRADE_TITLE
        keeper.category = 'trade'
        keeper.is_active = True
        keeper.save()
        trade_qs.exclude(pk=keeper.pk).update(is_active=False)

    # Same consolidation for the e-commerce program
    ecom_qs = TrainingProgram.objects.filter(title__in=ECOMMERCE_VARIANTS)
    if ecom_qs.exists():
        keeper = ecom_qs.filter(title=FINAL_ECOMMERCE_TITLE).first() or ecom_qs.first()
        keeper.title = FINAL_ECOMMERCE_TITLE
        keeper.category = 'enterprise'
        keeper.is_active = True
        keeper.save()
        ecom_qs.exclude(pk=keeper.pk).update(is_active=False)

    # Everything else (farming, financial, or any other stray program) gets
    # deactivated — site now offers only these two programs.
    TrainingProgram.objects.exclude(
        title__in=[FINAL_TRADE_TITLE, FINAL_ECOMMERCE_TITLE]
    ).update(is_active=False)


def reverse_update_training_programs(apps, schema_editor):
    # Not meaningfully reversible (original categories/titles of consolidated
    # duplicates aren't recoverable) — no-op on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_alter_trainingprogram_category'),
    ]

    operations = [
        migrations.RunPython(update_training_programs, reverse_update_training_programs),
    ]
