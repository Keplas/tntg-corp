from django.db import migrations


DEPARTMENTS = [
    {
        'name': 'Legal Services',
        'slug': 'legal',
        'icon': 'fas fa-balance-scale',
        'tagline': 'Qualified lawyers and paralegals for personal and business legal needs.',
        'description': (
            'T&TG\'s in-house legal team provides expert guidance on contracts, '
            'business formation, dispute resolution, immigration matters, and more. '
            'We serve individuals and businesses with clarity and confidentiality.'
        ),
        'is_active': True,
        'order': 1,
    },
    {
        'name': 'Software Engineering',
        'slug': 'software',
        'icon': 'fas fa-code',
        'tagline': 'Expert software engineers for web, mobile, and enterprise solutions.',
        'description': (
            'Our software engineers help you build, fix, and scale digital products. '
            'From custom web applications to automation scripts and API integrations, '
            'T&TG tech professionals deliver quality software on time.'
        ),
        'is_active': True,
        'order': 2,
    },
    {
        'name': 'Accounting & Finance',
        'slug': 'accounting',
        'icon': 'fas fa-calculator',
        'tagline': 'Professional accountants for bookkeeping, tax, and financial advisory.',
        'description': (
            'T&TG\'s accounting team handles bookkeeping, tax filing, financial '
            'statements, payroll, and business advisory. Whether you are a sole trader '
            'or a growing company, we keep your finances in order.'
        ),
        'is_active': True,
        'order': 3,
    },
    {
        'name': 'Human Resources',
        'slug': 'human-resources',
        'icon': 'fas fa-users',
        'tagline': 'HR professionals for hiring, compliance, and workforce management.',
        'description': (
            'Our HR specialists assist with recruitment, employment contracts, '
            'HR policy drafting, performance management, and regulatory compliance. '
            'Get professional HR support without hiring a full department.'
        ),
        'is_active': True,
        'order': 4,
    },
    {
        'name': 'Forex Consulting',
        'slug': 'forex',
        'icon': 'fas fa-chart-line',
        'tagline': 'Forex consultants for currency strategy and international payments.',
        'description': (
            'T&TG forex consultants guide businesses and individuals on foreign exchange '
            'strategy, currency risk management, remittances, and international payment '
            'optimisation. We operate across multiple currencies and corridors.'
        ),
        'is_active': True,
        'order': 5,
    },
    {
        'name': 'International Trade',
        'slug': 'trade',
        'icon': 'fas fa-globe',
        'tagline': 'Trade specialists for import, export, and cross-border commerce.',
        'description': (
            'Our international trade specialists help you navigate customs regulations, '
            'export documentation, import compliance, trade finance, and market entry '
            'strategies. We cover East Africa, Canada, Europe, and beyond.'
        ),
        'is_active': True,
        'order': 6,
    },
]


def seed_departments(apps, schema_editor):
    Department = apps.get_model('professionals', 'Department')
    for dept in DEPARTMENTS:
        Department.objects.get_or_create(slug=dept['slug'], defaults=dept)


def unseed_departments(apps, schema_editor):
    Department = apps.get_model('professionals', 'Department')
    slugs = [d['slug'] for d in DEPARTMENTS]
    Department.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('professionals', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_departments, reverse_code=unseed_departments),
    ]
