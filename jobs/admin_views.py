from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from .models import Job, JobSeeker, Employer, Application
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

def is_admin(user):
    return user.is_staff or user.is_superuser

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        # Get statistics
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        total_applications = Application.objects.count()
        pending_applications = Application.objects.filter(status='pending').count()
        total_job_seekers = JobSeeker.objects.count()
        total_employers = Employer.objects.count()
        
        # Get recent data
        recent_jobs = Job.objects.select_related('employer').order_by('-created_at')[:5]
        recent_applications = Application.objects.select_related('job_seeker', 'job').order_by('-applied_at')[:5]
        
        # Get this week's statistics
        seven_days_ago = timezone.now() - timedelta(days=7)
        jobs_this_week = Job.objects.filter(created_at__gte=seven_days_ago).count()
        applications_this_week = Application.objects.filter(applied_at__gte=seven_days_ago).count()
        
        # Get category statistics
        category_stats = Job.objects.values('category').annotate(count=Count('id')).order_by('-count')
        
        # Get province statistics
        province_stats = Job.objects.values('province').annotate(count=Count('id')).order_by('-count')[:10]
        
        context = {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'total_job_seekers': total_job_seekers,
            'total_employers': total_employers,
            'recent_jobs': recent_jobs,
            'recent_applications': recent_applications,
            'jobs_this_week': jobs_this_week,
            'applications_this_week': applications_this_week,
            'category_stats': category_stats,
            'province_stats': province_stats,
            'page': 'dashboard',
        }
        
        return render(request, 'dashboard.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ManageJobsView(View):
    def get(self, request):
        jobs = Job.objects.select_related('employer').order_by('-created_at')
        context = {
            'jobs': jobs,
            'page': 'manage_jobs'
        }
        return render(request, 'manage_jobs.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ManageApplicationsView(View):
    def get(self, request):
        status_filter = request.GET.get('status', '')
        applications = Application.objects.select_related('job_seeker', 'job').order_by('-applied_at')
        
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        context = {
            'applications': applications,
            'status_filter': status_filter,
            'page': 'manage_applications'
        }
        return render(request, 'manage_applications.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ManageUsersView(View):
    def get(self, request):
        job_seekers = JobSeeker.objects.select_related('user').order_by('-created_at')
        employers = Employer.objects.select_related('user').order_by('-created_at')
        
        context = {
            'job_seekers': job_seekers,
            'employers': employers,
            'page': 'manage_users'
        }
        return render(request, 'manage_users.html', context)
