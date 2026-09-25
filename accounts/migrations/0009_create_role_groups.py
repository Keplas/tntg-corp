from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    groups = {
        'Admin': [],
        'Staff': [],
        'B2B Partner': [],
        'Consumer': [],
    }

    for name in groups:
        Group.objects.get_or_create(name=name)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ['Admin', 'Staff', 'B2B Partner', 'Consumer']:
        Group.objects.filter(name=name).delete()


class Migration(migrations.Migration):
    dependencies = [('accounts', '0008_add_saved_cart_to_user')]
    operations = [migrations.RunPython(create_groups, remove_groups)]
