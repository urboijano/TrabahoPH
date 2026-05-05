from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from .models import Job, JobSeeker, Employer, Application
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .views import is_profile_complete, get_ai_recommended_jobs
from django.contrib import messages

def is_admin(user):
    return user.is_staff or user.is_superuser

def is_job_seeker(user):
    try:
        return hasattr(user, 'jobseeker')
    except:
        return False

def is_employer(user):
    try:
        return hasattr(user, 'employer')
    except:
        return False

# ======================== ADMIN DASHBOARD ========================

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        total_applications = Application.objects.count()
        pending_applications = Application.objects.filter(status='pending').count()
        total_job_seekers = JobSeeker.objects.count()
        total_employers = Employer.objects.count()
        
        recent_jobs = Job.objects.select_related('employer').order_by('-created_at')[:5]
        recent_applications = Application.objects.select_related('job_seeker', 'job').order_by('-applied_at')[:5]
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        jobs_this_week = Job.objects.filter(created_at__gte=seven_days_ago).count()
        applications_this_week = Application.objects.filter(applied_at__gte=seven_days_ago).count()
        
        category_stats = Job.objects.values('category').annotate(count=Count('id')).order_by('-count')
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
        
        return render(request, 'admin/dashboard.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ManageJobsView(View):
    def get(self, request):
        jobs = Job.objects.select_related('employer').order_by('-created_at')
        context = {
            'jobs': jobs,
            'page': 'manage_jobs'
        }
        return render(request, 'admin/manage_jobs.html', context)

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
        return render(request, 'admin/manage_applications.html', context)

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
        return render(request, 'admin/manage_users.html', context)

# ======================== JOB SEEKER DASHBOARD ========================

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_job_seeker), name='dispatch')
class SeekerDashboardView(View):
    def get(self, request):
        try:
            job_seeker = JobSeeker.objects.get(user=request.user)
        except JobSeeker.DoesNotExist:
            return redirect('index')
        
        total_applications = Application.objects.filter(job_seeker=job_seeker).count()
        pending_apps = Application.objects.filter(job_seeker=job_seeker, status='pending').count()
        accepted_apps = Application.objects.filter(job_seeker=job_seeker, status='accepted').count()
        rejected_apps = Application.objects.filter(job_seeker=job_seeker, status='rejected').count()
        
        recent_applications = Application.objects.filter(job_seeker=job_seeker).select_related('job').order_by('-applied_at')[:5]
        
        # Get all active jobs not yet applied by user
        all_available_jobs = Job.objects.filter(
            is_active=True
        ).exclude(
            applications__job_seeker=job_seeker
        ).select_related('employer')
        
        # Try to get AI-recommended jobs based on skills
        if job_seeker.skills:
            recommended_jobs = get_ai_recommended_jobs(job_seeker, all_available_jobs, limit=5)
        else:
            # Fallback to location-based recommendations if no skills
            recommended_jobs = list(all_available_jobs[:5])
        
        context = {
            'job_seeker': job_seeker,
            'total_applications': total_applications,
            'pending_count': pending_apps,
            'accepted_count': accepted_apps,
            'rejected_count': rejected_apps,
            'recent_applications': recent_applications,
            'recommended_jobs': recommended_jobs,
            'profile_complete': is_profile_complete(job_seeker),
        }
        
        return render(request, 'seeker_dashboard.html', context)

# ======================== EMPLOYER DASHBOARD ========================

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_employer), name='dispatch')
class EmployerDashboardView(View):
    def get(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
        except Employer.DoesNotExist:
            return redirect('index')
        
        total_jobs = Job.objects.filter(employer=employer).count()
        active_jobs = Job.objects.filter(employer=employer, is_active=True).count()
        total_applications = Application.objects.filter(job__employer=employer).count()
        pending_apps = Application.objects.filter(job__employer=employer, status='pending').count()
        accepted_apps = Application.objects.filter(job__employer=employer, status='accepted').count()
        
        recent_jobs = Job.objects.filter(employer=employer).order_by('-created_at')[:5]
        
        recent_applications = Application.objects.filter(
            job__employer=employer
        ).select_related('job_seeker', 'job').order_by('-applied_at')[:5]
        
        context = {
            'employer': employer,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'pending_count': pending_apps,
            'accepted_count': accepted_apps,
            'recent_jobs': recent_jobs,
            'recent_applications': recent_applications,
        }
        
        return render(request, 'employer_dashboard.html', context)

# ======================== EMPLOYER POST JOB ========================

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_employer), name='dispatch')
class PostJobView(View):
    def get(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
        except Employer.DoesNotExist:
            return redirect('index')
        
        categories = Job.CATEGORY_CHOICES
        
        context = {
            'employer': employer,
            'categories': categories,
        }
        
        return render(request, 'post_job.html', context)
    
    def post(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
        except Employer.DoesNotExist:
            return redirect('index')
        
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        location = request.POST.get('location', '').strip()
        barangay = request.POST.get('barangay', '').strip()
        salary = request.POST.get('salary', '').strip()
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Job title is required.')
        elif len(title) < 3:
            errors.append('Job title must be at least 3 characters.')
        elif len(title) > 200:
            errors.append('Job title cannot exceed 200 characters.')
        
        if not description:
            errors.append('Job description is required.')
        elif len(description) < 20:
            errors.append('Job description must be at least 20 characters.')
        
        if not category:
            errors.append('Job category is required.')
        
        if not location:
            errors.append('Exact location is required.')
        
        if not barangay:
            errors.append('Barangay is required.')
        
        if not salary:
            errors.append('Salary information is required.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'employer': employer,
                'categories': Job.CATEGORY_CHOICES,
                'form_data': request.POST,
            }
            return render(request, 'post_job.html', context)
        
        # Create job - use barangay for location fields
        try:
            job = Job.objects.create(
                title=title,
                employer=employer,
                description=description,
                category=category,
                location=location,
                province=employer.province,
                municipality=employer.municipality,
                barangay=barangay,
                salary=salary,
                is_active=True,
                is_approved=False  # Jobs require admin approval
            )
            
            messages.success(request, 'Job posted successfully! Your job listing is pending admin approval.')
            return redirect('employer_dashboard')
        
        except Exception as e:
            messages.error(request, f'An error occurred while posting the job: {str(e)}')
            context = {
                'employer': employer,
                'categories': Job.CATEGORY_CHOICES,
                'form_data': request.POST,
            }
            return render(request, 'post_job.html', context)
