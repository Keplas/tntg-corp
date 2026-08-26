from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('marketplace', '0015_add_display_currency_to_order')]
    operations = [
        migrations.RunSQL(
            # Indexes for frequently filtered fields
            sql=[
                "CREATE INDEX IF NOT EXISTS idx_product_is_active ON marketplace_product(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_product_category ON marketplace_product(category);",
                "CREATE INDEX IF NOT EXISTS idx_product_market_type ON marketplace_product(market_type);",
                "CREATE INDEX IF NOT EXISTS idx_order_buyer ON marketplace_order(buyer_id);",
                "CREATE INDEX IF NOT EXISTS idx_order_status ON marketplace_order(status);",
                "CREATE INDEX IF NOT EXISTS idx_order_created ON marketplace_order(created_at DESC);",
                "CREATE INDEX IF NOT EXISTS idx_ticket_email ON training_eventticket(email);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_product_is_active;",
                "DROP INDEX IF EXISTS idx_product_category;",
                "DROP INDEX IF EXISTS idx_product_market_type;",
                "DROP INDEX IF EXISTS idx_order_buyer;",
                "DROP INDEX IF EXISTS idx_order_status;",
                "DROP INDEX IF EXISTS idx_order_created;",
                "DROP INDEX IF EXISTS idx_ticket_email;",
            ]
        )
    ]
