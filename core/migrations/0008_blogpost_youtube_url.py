from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_blog_posts'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='youtube_url',
            field=models.URLField(
                blank=True,
                help_text='YouTube video URL for this post (e.g. https://youtu.be/abc123). '
                          'Embeds the video on the detail page and shows a video badge on the listing.'
            ),
        ),
    ]
