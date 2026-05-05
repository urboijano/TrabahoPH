from django.contrib import admin
from django.utils.html import format_html
from .models import JobSeeker, Employer, Job, Application
import logging

logger = logging.getLogger(__name__)


@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    """Admin interface for JobSeeker model"""
    
    list_display = ('get_full_name', 'mobile', 'province', 'municipality', 'barangay', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'mobile', 'province', 'skills')
    list_filter = ('province', 'municipality', 'created_at')
    readonly_fields = ('created_at', 'get_full_name', 'get_email')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_full_name', 'get_email')
        }),
        ('Contact Information', {
            'fields': ('mobile',)
        }),
        ('Location', {
            'fields': ('province', 'municipality', 'barangay')
        }),
        ('Professional', {
            'fields': ('skills',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_full_name(self, obj):
        """Display full name of the job seeker"""
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'
    
    def get_email(self, obj):
        """Display email address"""
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    """Admin interface for Employer model"""
    
    list_display = ('business_name', 'business_type', 'province', 'contact_number', 'get_dti_status', 'created_at')
    search_fields = ('business_name', 'contact_number', 'business_type', 'province', 'business_description')
    list_filter = ('business_type', 'province', 'municipality', 'created_at')
    readonly_fields = ('created_at', 'get_email')
    
    fieldsets = (
        ('Business Information', {
            'fields': ('user', 'business_name', 'business_type', 'business_description')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'get_email')
        }),
        ('Location', {
            'fields': ('province', 'municipality', 'barangay')
        }),
        ('Compliance', {
            'fields': ('dti_permit',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_email(self, obj):
        """Display email address"""
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_dti_status(self, obj):
        """Display DTI permit status"""
        if obj.dti_permit:
            return format_html('<span style="color: green;">✓ Submitted</span>')
        return format_html('<span style="color: red;">✗ Missing</span>')
    get_dti_status.short_description = 'DTI Permit Status'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for Job model"""
    
    list_display = ('title', 'employer', 'category', 'province', 'get_approval_badge', 'get_status_badge', 'application_count', 'created_at')
    search_fields = ('title', 'employer__business_name', 'description', 'location', 'province')
    list_filter = ('category', 'province', 'is_active', 'is_approved', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'application_count')
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'employer', 'description', 'category', 'salary')
        }),
        ('Location', {
            'fields': ('location', 'province', 'municipality', 'barangay')
        }),
        ('Status & Approval', {
            'fields': ('is_active', 'is_approved'),
            'description': 'Set is_approved=True to make this job visible in public listings'
        }),
        ('Statistics', {
            'fields': ('application_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['activate_jobs', 'deactivate_jobs', 'approve_jobs', 'reject_jobs']
    
    def get_status_badge(self, obj):
        """Display job status as colored badge"""
        if obj.is_active:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Active</span>')
        return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">Inactive</span>')
    get_status_badge.short_description = 'Status'
    
    def get_approval_badge(self, obj):
        """Display job approval status as colored badge"""
        if obj.is_approved:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Approved</span>')
        return format_html('<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">⏳ Pending Review</span>')
    get_approval_badge.short_description = 'Approval'
    
    def application_count(self, obj):
        """Display total number of applications for this job"""
        return obj.applications.count()
    application_count.short_description = 'Applications'
    
    def activate_jobs(self, request, queryset):
        """Action to activate multiple jobs"""
        count = queryset.update(is_active=True)
        logger.info(f"Admin {request.user} activated {count} jobs")
        self.message_user(request, f'{count} job(s) activated successfully.')
    activate_jobs.short_description = 'Activate selected jobs'
    
    def deactivate_jobs(self, request, queryset):
        """Action to deactivate multiple jobs"""
        count = queryset.update(is_active=False)
        logger.info(f"Admin {request.user} deactivated {count} jobs")
        self.message_user(request, f'{count} job(s) deactivated successfully.')
    deactivate_jobs.short_description = 'Deactivate selected jobs'
    
    def approve_jobs(self, request, queryset):
        """Action to approve multiple jobs for public display"""
        count = queryset.update(is_approved=True, is_active=True)
        logger.info(f"Admin {request.user} approved {count} jobs")
        self.message_user(request, f'{count} job(s) approved and activated successfully!')
    approve_jobs.short_description = '✓ Approve selected jobs'
    
    def reject_jobs(self, request, queryset):
        """Action to reject multiple jobs (keep them but mark as inactive)"""
        count = queryset.update(is_active=False)
        logger.info(f"Admin {request.user} rejected {count} jobs")
        self.message_user(request, f'{count} job(s) rejected and deactivated.')
    reject_jobs.short_description = '✗ Reject selected jobs'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application model"""
    
    list_display = ('get_applicant_name', 'job', 'get_status_badge', 'applied_at', 'employer_name')
    search_fields = ('job_seeker__user__first_name', 'job_seeker__user__last_name', 'job__title', 'job__employer__business_name')
    list_filter = ('status', 'applied_at', 'job__category', 'job__province')
    readonly_fields = ('applied_at', 'get_applicant_email', 'get_job_details')
    
    fieldsets = (
        ('Application Information', {
            'fields': ('job_seeker', 'job', 'get_applicant_email', 'status')
        }),
        ('Job Details', {
            'fields': ('get_job_details',),
            'classes': ('collapse',)
        }),
        ('Timeline', {
            'fields': ('applied_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-applied_at',)
    date_hierarchy = 'applied_at'
    actions = ['accept_applications', 'reject_applications', 'pending_applications']
    
    def get_applicant_name(self, obj):
        """Display applicant name"""
        user = obj.job_seeker.user
        return f"{user.first_name} {user.last_name}"
    get_applicant_name.short_description = 'Applicant Name'
    
    def get_applicant_email(self, obj):
        """Display applicant email"""
        return obj.job_seeker.user.email
    get_applicant_email.short_description = 'Applicant Email'
    
    def employer_name(self, obj):
        """Display employer name"""
        return obj.job.employer.business_name
    employer_name.short_description = 'Employer'
    
    def get_job_details(self, obj):
        """Display job details"""
        job = obj.job
        return f"""
        <strong>Job:</strong> {job.title}<br/>
        <strong>Employer:</strong> {job.employer.business_name}<br/>
        <strong>Category:</strong> {job.category}<br/>
        <strong>Salary:</strong> {job.salary}<br/>
        <strong>Location:</strong> {job.location}, {job.province}
        """
    get_job_details.short_description = 'Job Details'
    
    def get_status_badge(self, obj):
        """Display application status as colored badge"""
        color_map = {
            'pending': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545'
        }
        color = color_map.get(obj.status, '#6c757d')
        status_text = obj.get_status_display()
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 3px;">{status_text}</span>'
        )
    get_status_badge.short_description = 'Status'
    
    def accept_applications(self, request, queryset):
        """Action to accept multiple applications and trigger notifications"""
        count = 0
        for application in queryset:
            application.status = 'accepted'
            application.save()  # Triggers post_save signal with email
            count += 1
        logger.info(f"Admin {request.user} accepted {count} applications")
        self.message_user(request, f'{count} application(s) accepted and emails sent.')
    accept_applications.short_description = '✓ Accept selected applications (sends email)'
    
    def reject_applications(self, request, queryset):
        """Action to reject multiple applications and trigger notifications"""
        count = 0
        for application in queryset:
            application.status = 'rejected'
            application.save()  # Triggers post_save signal with email
            count += 1
        logger.info(f"Admin {request.user} rejected {count} applications")
        self.message_user(request, f'{count} application(s) rejected and emails sent.')
    reject_applications.short_description = '✗ Reject selected applications (sends email)'
    
    def pending_applications(self, request, queryset):
        """Action to mark applications as pending"""
        count = queryset.update(status='pending')
        logger.info(f"Admin {request.user} marked {count} applications as pending")
        self.message_user(request, f'{count} application(s) marked as pending.')
    pending_applications.short_description = 'Mark as pending'

