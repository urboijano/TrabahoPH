"""Django signals for jobs app - Handle post-save events"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Application
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Application)
def notify_application_status_change(sender, instance, created, **kwargs):
    """
    Send email notification to job seeker when application status changes
    """
    
    # Only send email if status changed (not on creation with pending status)
    if created:
        logger.info(f"New application created: {instance.job_seeker.user.email} for {instance.job.title}")
        return
    
    # Only send email for accepted or rejected status
    if instance.status not in ['accepted', 'rejected']:
        return
    
    # Prepare email data
    job_seeker = instance.job_seeker
    user_email = job_seeker.user.email
    job_title = instance.job.title
    employer_name = instance.job.employer.business_name
    status_display = instance.get_status_display()
    
    # Create email content based on status
    if instance.status == 'accepted':
        subject = f'Great News! Your application for {job_title} has been accepted!'
        message = f"""
Dear {job_seeker.user.first_name},

Congratulations! Your application for the position of {job_title} at {employer_name} has been accepted!

The employer will contact you soon with further details. Make sure your phone number {job_seeker.mobile} is up to date.

Best regards,
TrabahoPH Team
        """
        
    elif instance.status == 'rejected':
        subject = f'Update on Your Application for {job_title}'
        message = f"""
Dear {job_seeker.user.first_name},

Thank you for your interest in the {job_title} position at {employer_name}. Unfortunately, your application has not been selected at this time.

We encourage you to keep exploring other opportunities on TrabahoPH. Don't give up!

Best regards,
TrabahoPH Team
        """
    else:
        subject = f'Your Application Status Has Been Updated'
        message = f"""
Dear {job_seeker.user.first_name},

Your application for {job_title} at {employer_name} has been updated to: {status_display}.

Log in to your account to view more details.

Best regards,
TrabahoPH Team
        """
    
    # Send email
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {user_email} about application status change to {instance.status}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")
