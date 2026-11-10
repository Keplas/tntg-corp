from django.db import migrations
from decimal import Decimal


PACKAGES = {
    # ── LEGAL SERVICES ────────────────────────────────────────────────────
    'legal': [
        {
            'name': 'Initial Legal Consultation',
            'service_type': 'consultation',
            'description': (
                'A focused one-on-one session with a T&TG lawyer or paralegal to assess '
                'your legal situation, understand your rights, and map out your options. '
                'Ideal for individuals or businesses facing a new legal question.'
            ),
            'deliverables': (
                'Written summary of legal position\n'
                'Recommended course of action\n'
                'List of documents or evidence to gather\n'
                'Follow-up action plan'
            ),
            'duration': '60 minutes',
            'price': Decimal('95.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Contract Review & Drafting',
            'service_type': 'document_prep',
            'description': (
                'Our legal team reviews, drafts, or redlines any commercial or personal '
                'contract — service agreements, NDAs, employment contracts, lease agreements, '
                'and more. Returned with tracked changes and a plain-English summary.'
            ),
            'deliverables': (
                'Full contract review with tracked comments\n'
                'Plain-English risk summary\n'
                'Suggested amendments or redlines\n'
                'Final clean copy (if drafting)'
            ),
            'duration': '2–4 business days',
            'price': Decimal('380.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 2,
        },
        {
            'name': 'Business Formation Package',
            'service_type': 'project',
            'description': (
                'End-to-end legal support for registering your business — from choosing '
                'the right structure (sole proprietor, corporation, partnership) to filing '
                'with the appropriate authority and setting up governance documents.'
            ),
            'deliverables': (
                'Business structure recommendation\n'
                'Articles of incorporation or registration documents\n'
                'Shareholder or partnership agreement\n'
                'CRA business number registration guidance\n'
                'Registered address confirmation'
            ),
            'duration': '5–7 business days',
            'price': Decimal('850.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 3,
        },
        {
            'name': 'Monthly Legal Retainer',
            'service_type': 'retainer',
            'description': (
                'Ongoing monthly legal support for businesses that need reliable access '
                'to a lawyer or paralegal — covering contract queries, compliance questions, '
                'correspondence review, and urgent consultations throughout the month.'
            ),
            'deliverables': (
                'Up to 4 hours of legal consultation per month\n'
                'Unlimited email Q&A (responses within 24 hrs)\n'
                '2 contract reviews per month\n'
                'Monthly legal health check summary'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('1500.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],

    # ── SOFTWARE ENGINEERING ───────────────────────────────────────────────
    'software': [
        {
            'name': 'Technical Consultation',
            'service_type': 'consultation',
            'description': (
                'A focused session with a T&TG software engineer to review your tech '
                'stack, troubleshoot a problem, evaluate an architecture, or scope out '
                'a new feature. Useful for technical founders and product teams alike.'
            ),
            'deliverables': (
                'Technical assessment notes\n'
                'Recommended solution or approach\n'
                'Technology stack recommendations\n'
                'Estimated effort breakdown'
            ),
            'duration': '60 minutes',
            'price': Decimal('120.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Bug Fix & Code Review',
            'service_type': 'project',
            'description': (
                'Share your codebase or describe the bug and our engineer will diagnose, '
                'fix, and document the issue. Includes a code review report highlighting '
                'any other risks or improvements spotted along the way.'
            ),
            'deliverables': (
                'Root cause analysis report\n'
                'Fixed and tested code\n'
                'Code review notes with recommendations\n'
                'Documentation of changes made'
            ),
            'duration': '1–3 business days',
            'price': Decimal('280.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 2,
        },
        {
            'name': 'Web Application Development',
            'service_type': 'project',
            'description': (
                'Custom web application built to your specification by our in-house '
                'engineering team. From landing pages and e-commerce stores to dashboards '
                'and internal tools — scoped, quoted, and delivered on a fixed timeline.'
            ),
            'deliverables': (
                'Requirements and wireframe sign-off\n'
                'Fully functional web application\n'
                'Mobile-responsive design\n'
                'Deployment to your hosting environment\n'
                'Source code and documentation handover\n'
                '30-day post-launch support'
            ),
            'duration': 'Project-based — quoted per scope',
            'price': Decimal('2500.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 3,
        },
        {
            'name': 'Monthly Tech Support Retainer',
            'service_type': 'retainer',
            'description': (
                'Dedicated monthly engineering support — bug fixes, feature updates, '
                'performance monitoring, and advice from a senior T&TG engineer who '
                'knows your codebase.'
            ),
            'deliverables': (
                'Up to 8 hours of engineering work per month\n'
                'Priority bug fixes (response within 4 hrs)\n'
                'Monthly performance and security review\n'
                'Unlimited technical Q&A via email'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('950.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],

    # ── ACCOUNTING & FINANCE ───────────────────────────────────────────────
    'accounting': [
        {
            'name': 'Financial Consultation',
            'service_type': 'consultation',
            'description': (
                'One-on-one session with a T&TG accountant to review your financial '
                'position, understand your obligations, or plan for a major financial '
                'decision — whether personal or business.'
            ),
            'deliverables': (
                'Financial health summary\n'
                'Tax efficiency recommendations\n'
                'Action list with priorities\n'
                'Referral to specialist if needed'
            ),
            'duration': '60 minutes',
            'price': Decimal('95.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Tax Return Preparation',
            'service_type': 'document_prep',
            'description': (
                'Our certified accountants prepare your personal or corporate tax return '
                'accurately and on time — minimising your liability through eligible '
                'deductions while ensuring full CRA compliance.'
            ),
            'deliverables': (
                'Completed T1 (personal) or T2 (corporate) return\n'
                'Review of prior year discrepancies\n'
                'Deduction maximisation report\n'
                'Filed directly with CRA on your behalf\n'
                'CRA confirmation receipt'
            ),
            'duration': '3–5 business days',
            'price': Decimal('320.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 2,
        },
        {
            'name': 'Bookkeeping Setup & Clean-up',
            'service_type': 'project',
            'description': (
                'Set up your chart of accounts, migrate historical transactions, reconcile '
                'bank statements, and hand you a clean, audit-ready set of books. '
                'Covers up to 12 months of transaction history.'
            ),
            'deliverables': (
                'Chart of accounts configured\n'
                'Up to 12 months of transactions entered and categorised\n'
                'Bank and credit card reconciliation\n'
                'Profit & loss and balance sheet reports\n'
                'QuickBooks / Wave setup guide'
            ),
            'duration': '5–10 business days',
            'price': Decimal('680.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 3,
        },
        {
            'name': 'Monthly Bookkeeping Retainer',
            'service_type': 'retainer',
            'description': (
                'Hands-off monthly bookkeeping — we categorise your transactions, reconcile '
                'your accounts, and deliver clean financial reports every month so you '
                'always know where your business stands.'
            ),
            'deliverables': (
                'Monthly transaction entry and categorisation\n'
                'Bank and credit card reconciliation\n'
                'Monthly P&L and balance sheet\n'
                'HST/GST remittance preparation\n'
                'Year-end package ready for tax filing'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('480.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],

    # ── HUMAN RESOURCES ───────────────────────────────────────────────────
    'human-resources': [
        {
            'name': 'HR Consultation',
            'service_type': 'consultation',
            'description': (
                'Talk through a specific HR challenge with a T&TG HR professional — '
                'a disciplinary issue, a termination question, a hiring decision, '
                'or a compliance concern. Clear, practical advice grounded in '
                'Canadian employment standards.'
            ),
            'deliverables': (
                'Written summary of advice given\n'
                'Recommended next steps\n'
                'Relevant legislation references\n'
                'Template or checklist if applicable'
            ),
            'duration': '60 minutes',
            'price': Decimal('95.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Employment Contract & Offer Letter',
            'service_type': 'document_prep',
            'description': (
                'Custom employment contracts or offer letters drafted to your specifications — '
                'full-time, part-time, fixed-term, or contractor agreements. '
                'Compliant with the applicable Employment Standards Act.'
            ),
            'deliverables': (
                'Drafted employment contract or offer letter\n'
                'Non-compete / NDA clauses (if required)\n'
                'Probation and termination provisions\n'
                'Plain-English explanation of key clauses\n'
                'Editable Word version for your records'
            ),
            'duration': '2–3 business days',
            'price': Decimal('290.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 2,
        },
        {
            'name': 'HR Policy Development',
            'service_type': 'project',
            'description': (
                'Build a complete HR policy framework for your business — covering '
                'code of conduct, leave policies, anti-harassment, remote work, '
                'performance management, and more. Tailored to your size and industry.'
            ),
            'deliverables': (
                'HR policy handbook (up to 10 policies)\n'
                'Employee acknowledgement form\n'
                'Manager guide for each policy\n'
                'Onboarding checklist\n'
                'All documents in editable format'
            ),
            'duration': '7–10 business days',
            'price': Decimal('1250.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 3,
        },
        {
            'name': 'Monthly HR Support Retainer',
            'service_type': 'retainer',
            'description': (
                'On-call HR support for small and medium businesses without a dedicated '
                'HR department. Get answers to employee questions, help with hiring, '
                'and guidance on employment issues as they arise — every month.'
            ),
            'deliverables': (
                'Up to 4 hours of HR consultation per month\n'
                'Unlimited email Q&A (24-hr response)\n'
                '1 contract or policy document per month\n'
                'Monthly HR compliance update summary'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('720.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],

    # ── FOREX CONSULTING ──────────────────────────────────────────────────
    'forex': [
        {
            'name': 'Forex Strategy Consultation',
            'service_type': 'consultation',
            'description': (
                'A focused session to review your current foreign exchange exposure, '
                'discuss currency risk, and explore strategies to optimise your '
                'international payments and remittances. Suitable for individuals '
                'and import/export businesses.'
            ),
            'deliverables': (
                'Currency exposure summary\n'
                'Risk assessment (high/medium/low)\n'
                'Recommended hedging or payment strategy\n'
                'Best-rate corridor recommendations'
            ),
            'duration': '60 minutes',
            'price': Decimal('110.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Currency Risk Assessment Report',
            'service_type': 'document_prep',
            'description': (
                'A written assessment of your business\'s exposure to currency fluctuation — '
                'including your key trading pairs, historical volatility analysis, and a '
                'recommended hedging approach with cost estimates.'
            ),
            'deliverables': (
                'Currency exposure analysis (all active pairs)\n'
                'Historical volatility report (12 months)\n'
                'Hedging options with cost comparison\n'
                'Recommended payment timing strategy\n'
                'Written action plan'
            ),
            'duration': '2–4 business days',
            'price': Decimal('340.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 2,
        },
        {
            'name': 'International Payment Setup',
            'service_type': 'project',
            'description': (
                'End-to-end setup of an optimised international payment corridor for '
                'your business — selecting the right payment rails, reducing fees, '
                'ensuring compliance, and setting up recurring payment flows.'
            ),
            'deliverables': (
                'Payment corridor analysis and recommendation\n'
                'Provider comparison and account setup support\n'
                'Compliance and documentation checklist\n'
                'Recurring payment schedule configuration\n'
                'Staff training on payment process (1 hr)'
            ),
            'duration': '3–5 business days',
            'price': Decimal('550.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 3,
        },
        {
            'name': 'Monthly Forex Advisory',
            'service_type': 'retainer',
            'description': (
                'Monthly forex advisory for businesses with regular cross-border '
                'transactions. We monitor your key currency pairs, alert you to '
                'rate opportunities, and advise on timing and strategy throughout '
                'the month.'
            ),
            'deliverables': (
                'Monthly currency market brief\n'
                'Rate opportunity alerts (email/WhatsApp)\n'
                'Up to 3 hours of advisory consultation\n'
                'Monthly payment performance review\n'
                'Quarterly hedging strategy update'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('880.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],

    # ── INTERNATIONAL TRADE ────────────────────────────────────────────────
    'trade': [
        {
            'name': 'Trade Consultation',
            'service_type': 'consultation',
            'description': (
                'A one-on-one session with a T&TG trade specialist to assess your '
                'import or export situation — covering customs requirements, duties, '
                'trade agreements, documentation, and market entry considerations.'
            ),
            'deliverables': (
                'Trade situation summary\n'
                'Key regulatory requirements\n'
                'Duty and tariff overview\n'
                'Recommended next steps'
            ),
            'duration': '60 minutes',
            'price': Decimal('110.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 1,
        },
        {
            'name': 'Export Documentation Package',
            'service_type': 'document_prep',
            'description': (
                'Full preparation of export documentation for a single shipment — '
                'commercial invoice, packing list, certificate of origin, bill of lading '
                'instructions, and any destination-country compliance documents.'
            ),
            'deliverables': (
                'Commercial invoice\n'
                'Packing list\n'
                'Certificate of origin\n'
                'Bill of lading instructions\n'
                'Phytosanitary or compliance certificate (if required)\n'
                'HS code classification report'
            ),
            'duration': '2–4 business days',
            'price': Decimal('460.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 2,
        },
        {
            'name': 'Market Entry Strategy',
            'service_type': 'project',
            'description': (
                'A full market entry plan for exporting your product or service to a '
                'new country — covering regulatory requirements, tariffs, local '
                'competition, distribution options, and a go-to-market roadmap. '
                'T&TG covers East Africa, Canada, the EU, and the Middle East.'
            ),
            'deliverables': (
                'Target market analysis (2 countries compared)\n'
                'Regulatory and customs requirements report\n'
                'Competitive landscape overview\n'
                'Distribution and logistics options\n'
                'Go-to-market roadmap with timeline\n'
                'Risk assessment matrix'
            ),
            'duration': '10–14 business days',
            'price': Decimal('1900.00'),
            'currency': 'CAD',
            'is_featured': True,
            'order': 3,
        },
        {
            'name': 'Monthly Trade Advisory',
            'service_type': 'retainer',
            'description': (
                'Ongoing trade advisory for businesses with active import or export '
                'operations — covering compliance updates, shipment documentation '
                'review, supplier/buyer vetting, and strategic guidance every month.'
            ),
            'deliverables': (
                'Monthly trade regulatory update\n'
                'Up to 4 hours of advisory consultation\n'
                'Document review for up to 2 shipments\n'
                'Supplier or buyer due diligence (1 per month)\n'
                'Quarterly trade strategy review'
            ),
            'duration': 'Ongoing — billed monthly',
            'price': Decimal('1250.00'),
            'currency': 'CAD',
            'is_featured': False,
            'order': 4,
        },
    ],
}


def seed_packages(apps, schema_editor):
    Department = apps.get_model('professionals', 'Department')
    ServicePackage = apps.get_model('professionals', 'ServicePackage')

    for dept_slug, pkgs in PACKAGES.items():
        try:
            dept = Department.objects.get(slug=dept_slug)
        except Department.DoesNotExist:
            continue
        for pkg in pkgs:
            ServicePackage.objects.get_or_create(
                department=dept,
                name=pkg['name'],
                defaults={**pkg},
            )


def unseed_packages(apps, schema_editor):
    ServicePackage = apps.get_model('professionals', 'ServicePackage')
    names = [p['name'] for pkgs in PACKAGES.values() for p in pkgs]
    ServicePackage.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('professionals', '0002_seed_departments'),
    ]

    operations = [
        migrations.RunPython(seed_packages, reverse_code=unseed_packages),
    ]
