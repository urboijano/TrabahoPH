"""
Migration: Add profile image to JobSeeker
"""

from django.db import migrations, models
import jobs.validators


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_job_moderation'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobseeker',
            name='profile_image',
            field=models.ImageField(
                blank=True,
                help_text='Profile picture (JPG or PNG, max 2MB)',
                null=True,
                upload_to='profile_images/',
                validators=[jobs.validators.validate_profile_image]
            ),
        ),
        migrations.AddField(
            model_name='jobseeker',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
