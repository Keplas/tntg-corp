from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_partnership_application'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FranchiseeProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('franchise_type', models.CharField(choices=[('cafe_kiosk', 'Café / Kiosk Franchise'), ('distribution', 'Distribution Partner'), ('online_reseller', 'Online Reseller'), ('corporate_supply', 'Corporate & Institutional Supply'), ('mobile_unit', 'Mobile Coffee Unit')], max_length=30)),
                ('business_name', models.CharField(blank=True, help_text='Trading name e.g. "T&TG Kampala North". Leave blank to auto-generate.', max_length=200)),
                ('photo', models.URLField(blank=True, help_text='Profile photo URL')),
                ('territory', models.CharField(help_text='Named region e.g. "Kampala North", "Toronto West"', max_length=200)),
                ('zone', models.CharField(blank=True, help_text='Sub-division e.g. "Zone A", "Eastern Corridor"', max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('operational_status', models.CharField(choices=[('setup', 'Setting Up'), ('active', 'Active'), ('paused', 'Paused'), ('terminated', 'Terminated')], default='setup', max_length=20)),
                ('hq_notes', models.TextField(blank=True, help_text='Internal notes — not visible to franchisee')),
                ('approved_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='franchisee_profile', to='services.franchiseapplication')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='franchisee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Franchisee Profile',
                'verbose_name_plural': 'Franchisee Profiles',
                'ordering': ['-approved_at'],
            },
        ),
    ]
