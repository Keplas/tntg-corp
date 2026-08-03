from django.db import migrations
from django.utils import timezone

POSTS = [
    dict(
        title="T&TG Trade Corporation: Connecting Uganda's Coffee to the World",
        slug="tntg-connecting-ugandas-coffee-to-the-world",
        content="""T&TG Trade Corporation, headquartered in Toronto, Ontario, Canada, is proud to be a bridge between Uganda's world-class Arabica and Robusta green coffee and buyers across Canada, USA, Netherlands and Japan.

Uganda is one of Africa's largest coffee producers, and T&TG works directly with suppliers in Kampala and the surrounding regions to source premium quality beans that meet international standards. Every shipment is traceable from farm to port, with full phytosanitary certification and compliance with the Canadian Food Inspection Agency (CFIA) requirements.

Our mission is simple: connect producers, create trade opportunities, and reward everyone in the supply chain through our T&TG Loyalty Points Programme.

Whether you are a Canadian roaster looking for consistent supply, a Japanese importer seeking premium Ugandan Arabica, or a Kenyan distributor, T&TG is your trusted trade partner.""",
        excerpt="T&TG Trade Corp connects Uganda's premium Arabica and Robusta coffee to Canada, USA, Netherlands and Japan. Learn how we bridge the global coffee supply chain.",
        is_published=True,
        category="trade",
    ),
    dict(
        title="How T&TG Loyalty Points Work: Earn 0.5% on Every Purchase",
        slug="how-tntg-loyalty-points-work",
        content="""The T&TG Loyalty Programme is one of the most straightforward reward systems in the coffee trading industry. Here is how it works:

**Consumer Rate (0.5%):** Every time you purchase a T&TG product on our shopping platform, you earn 0.5% of the order value as T&TG Loyalty Points. These points accumulate in your account and can be converted to wallet credits on Day 45 after the qualifying purchase.

**Referral Rate (1%):** When you refer a friend or business partner to T&TG and they make a purchase using your referral code, you earn 1% of their order value as T&TG Loyalty Points.

**Withdrawal:** All withdrawal requests are processed on the Day 45 cycle and require your 4-digit security PIN. Funds can be withdrawn via Bank Transfer, MTN Mobile Money, Airtel Money or Stripe Payout.

**Multi-Currency Wallet:** T&TG's wallet supports CAD, USD, UGX, KES, EUR and JPY balances simultaneously, with live currency conversion using Bank of Canada-referenced rates.

The loyalty programme is governed by Canadian law and complies with Ontario's Consumer Protection Act, 2002.""",
        excerpt="Learn how T&TG Loyalty Points work — earn 0.5% per purchase, 1% per referral, withdraw on Day 45. Multi-currency wallet supporting CAD, USD, UGX, KES, EUR and JPY.",
        is_published=True,
        category="loyalty",
    ),
    dict(
        title="Understanding Live Forex Rates at T&TG: CAD, USD, UGX, KES, EUR and JPY",
        slug="understanding-live-forex-rates-tntg",
        content="""T&TG Trade Corporation operates across six countries — Canada, USA, Uganda, Kenya, Netherlands and Japan — which means currency exchange is at the heart of everything we do.

Our live forex platform provides real-time exchange rates for the following pairs: CAD/UGX, CAD/KES, USD/CAD, USD/UGX, USD/KES, EUR/CAD, JPY/CAD and UGX/KES. These rates are sourced from the Open Exchange Rates API and updated hourly.

**Important Legal Disclaimer:** All exchange rates displayed on the T&TG platform are for informational purposes only. The final exchange rate applied to your transaction is determined by your credit card issuer or payment processor (Stripe or Flutterwave). For Canadian tax and accounting purposes, all T&TG revenue is converted to Canadian Dollars (CAD) using the Bank of Canada Daily Exchange Rates Lookup Tool, as required by the Canada Revenue Agency (CRA).

This complies with Ontario's Consumer Protection Act, 2002, which requires transparent disclosure of all charges before a transaction is completed.""",
        excerpt="T&TG provides live CAD/UGX, CAD/KES, EUR/CAD and JPY/CAD forex rates. Learn about our Ontario Consumer Protection Act compliant rate display and CRA accounting.",
        is_published=True,
        category="forex",
    ),
    dict(
        title="Partner With T&TG: Coffee Suppliers, Distributors and Regional Managers",
        slug="partner-with-tntg-coffee-trade",
        content="""T&TG Trade Corporation is actively seeking trade partners across our six operating countries to grow the coffee supply chain.

**Coffee Suppliers (Uganda & Kenya):** If you are a coffee farmer, cooperative or processor in Uganda or Kenya with access to quality Arabica or Robusta green coffee, we want to hear from you. T&TG offers seller agreements with transparent pricing, full documentation support, and payment on agreed terms.

**Distributors (Canada, USA, Netherlands, Japan):** If you are a coffee roaster, importer or distributor in Canada, USA, Netherlands or Japan looking for a consistent supply of premium Ugandan green coffee, T&TG can fulfill your volume requirements with full export documentation.

**Regional Managers:** T&TG is building a regional management network in Africa and Japan to coordinate local purchases, manage small business clients and ensure accountability at every level of the supply chain.

To apply, visit our Trade Application page or contact Tom Ssembiito directly at tom.grouptrade@gmail.com or WhatsApp +1 (416) 832 3512.""",
        excerpt="T&TG seeks coffee suppliers in Uganda/Kenya, distributors in Canada/USA/Netherlands/Japan, and regional managers for Africa and Japan. Apply to partner with us.",
        is_published=True,
        category="trade",
    ),
]

def add_posts(apps, schema_editor):
    BlogPost = apps.get_model('core', 'BlogPost')
    for d in POSTS:
        if not BlogPost.objects.filter(slug=d['slug']).exists():
            BlogPost.objects.create(**d)

class Migration(migrations.Migration):
    dependencies = [('core', '0006_deactivate_irrelevant_training')]
    operations   = [migrations.RunPython(add_posts, migrations.RunPython.noop)]
