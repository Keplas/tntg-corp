from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('marketplace', '0013_add_product_country_price')]
    operations = [
        migrations.AddField(
            model_name='order',
            name='display_currency',
            field=models.CharField(blank=True, default='', max_length=5, help_text='Currency chosen by buyer at checkout'),
        ),
        migrations.AddField(
            model_name='order',
            name='display_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, help_text='Total in buyer chosen currency'),
        ),
    ]
