from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_withdrawal_approval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='country',
            field=models.CharField(
                max_length=2,
                blank=True,
                choices=[
                    ('CA', 'Canada'),
                    ('UG', 'Uganda'),
                    ('KE', 'Kenya'),
                    ('US', 'United States (Ohio)'),
                ],
            ),
        ),
    ]
