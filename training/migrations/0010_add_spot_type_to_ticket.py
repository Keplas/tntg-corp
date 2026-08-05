from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('training', '0009_seed_training_events')]
    operations = [
        migrations.AddField(
            model_name='eventticket',
            name='spot_type',
            field=models.CharField(
                max_length=20,
                choices=[('in_person','Reserve a Spot (In-Person)'),('online','Online Spot (Virtual)')],
                default='online',
            ),
        ),
    ]
