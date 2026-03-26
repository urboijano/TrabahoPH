from django.contrib import admin
from .models import JobSeeker, Employer, Job, Application

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'mobile', 'province', 'barangay', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'mobile')
    list_filter = ('province', 'municipality', 'created_at')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'business_type', 'province', 'contact_number', 'created_at')
    search_fields = ('business_name', 'contact_number')
    list_filter = ('business_type', 'province', 'created_at')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'province', 'is_active', 'created_at')
    search_fields = ('title', 'employer__business_name')
    list_filter = ('category', 'province', 'is_active', 'created_at')
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'employer', 'description', 'category', 'salary')
        }),
        ('Location', {
            'fields': ('location', 'province', 'municipality', 'barangay')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'job', 'status', 'applied_at')
    search_fields = ('job_seeker__user__first_name', 'job__title')
    list_filter = ('status', 'applied_at')
    readonly_fields = ('applied_at',)
