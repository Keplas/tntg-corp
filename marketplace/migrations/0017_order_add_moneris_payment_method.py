from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0016_add_performance_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                blank=True,
                max_length=14,
                choices=[
                    ('card',         'Card (Stripe)'),
                    ('mobile_money', 'Mobile Money (Flutterwave)'),
                    ('moneris',      'Card — Canada (Moneris)'),
                    ('manual',       'Bank Transfer / Manual'),
                ],
            ),
        ),
    ]
