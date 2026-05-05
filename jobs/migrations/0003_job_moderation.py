"""
Migration: Add job moderation fields
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_remove_jobseeker_sms_alerts_employer_dti_permit'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_approved',
            field=models.BooleanField(
                default=False,
                help_text='Job post requires admin approval before it appears in listings'
            ),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['-created_at'], name='jobs_job_c_creat_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['is_active', 'is_approved'], name='jobs_job_is_ac_idx'),
        ),
    ]
