from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_add_security_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avonpointtransaction',
            name='status',
            field=models.CharField(
                max_length=20,
                default='pending_approval',
                choices=[
                    ('pending_approval', 'Pending Admin Approval'),
                    ('approved',         'Approved — Processing'),
                    ('completed',        'Paid Out'),
                    ('rejected',         'Rejected'),
                ],
            ),
        ),
        # Migrate any legacy 'pending' rows to 'pending_approval'
        migrations.RunSQL(
            "UPDATE accounts_avonpointtransaction SET status='pending_approval' WHERE status='pending';",
            reverse_sql="UPDATE accounts_avonpointtransaction SET status='pending' WHERE status='pending_approval';"
        ),
        migrations.RunSQL(
            "UPDATE accounts_avonpointtransaction SET status='rejected' WHERE status='not_accepted';",
            reverse_sql="UPDATE accounts_avonpointtransaction SET status='not_accepted' WHERE status='rejected';"
        ),
    ]
