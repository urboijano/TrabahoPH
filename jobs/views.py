from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Job, JobSeeker, Employer, Application

class IndexView(View):
    def get(self, request):
        jobs = Job.objects.filter(is_active=True)[:6]
        context = {
            'jobs': jobs,
            'user': request.user,
            'is_authenticated': request.user.is_authenticated
        }
        return render(request, 'index.html', context)

class AuthView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        context = {}
        return render(request, 'auth.html', context)

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        context = {'show_register': True}
        return render(request, 'register.html', context)

class LoginView(View):
    def post(self, request):
        login_input = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        # Try to authenticate with email first, then username
        user = None
        try:
            user_obj = User.objects.get(email=login_input)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            # Try with username if email doesn't exist
            user = authenticate(request, username=login_input, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Redirect based on user type
            if user.is_staff:
                return redirect('admin_dashboard')
            elif hasattr(user, 'jobseeker'):
                return redirect('seeker_dashboard')
            elif hasattr(user, 'employer'):
                return redirect('employer_dashboard')
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials.')
        
        return redirect('auth')

class RegisterJobSeekerView(View):
    def post(self, request):
        full_name = request.POST.get('fullName', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        province = request.POST.get('province', '').strip()
        skills = request.POST.get('skills', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        
        # Validation
        if not all([full_name, email, phone, province, password]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login or use a different email.')
            return redirect('register')
        
        try:
            # Create user
            username = email.split('@')[0] + str(User.objects.count())
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0] if full_name else 'User'
            )
            
            # Create job seeker profile
            JobSeeker.objects.create(
                user=user,
                phone=phone,
                province=province,
                skills=skills
            )
            
            messages.success(request, 'Registration successful! Please log in with your credentials.')
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'Registration failed. Please try again. {str(e)}')
            return redirect('register')

class RegisterEmployerView(View):
    def post(self, request):
        business_name = request.POST.get('businessName', '').strip()
        contact_person = request.POST.get('contactPerson', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        province = request.POST.get('province', '').strip()
        business_description = request.POST.get('businessDescription', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        
        # Validation
        if not all([business_name, contact_person, email, phone, province, password]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login or use a different email.')
            return redirect('register')
        
        try:
            # Create user
            username = business_name.replace(' ', '')[:15] + str(User.objects.count())
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=contact_person
            )
            
            # Create employer profile
            Employer.objects.create(
                user=user,
                business_name=business_name,
                contact_person=contact_person,
                phone=phone,
                province=province,
                description=business_description
            )
            
            messages.success(request, 'Registration successful! Please log in with your credentials.')
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'Registration failed. Please try again. {str(e)}')
            return redirect('register')

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('index')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('index')

class JobListView(View):
    def get(self, request):
        jobs = Job.objects.filter(is_active=True)
        province_filter = request.GET.get('province', '')
        category_filter = request.GET.get('category', '')
        search_query = request.GET.get('q', '')
        
        if province_filter:
            jobs = jobs.filter(province=province_filter)
        if category_filter:
            jobs = jobs.filter(category=category_filter)
        if search_query:
            jobs = jobs.filter(location__icontains=search_query) | jobs.filter(province__icontains=search_query)
        
        return render(request, 'job_list.html', {'jobs': jobs})

@method_decorator(login_required, name='dispatch')
class ApplyJobView(View):
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
            job_seeker = JobSeeker.objects.get(user=request.user)
            
            application, created = Application.objects.get_or_create(
                job_seeker=job_seeker,
                job=job
            )
            
            if created:
                return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'You have already applied for this job.'})
        except (Job.DoesNotExist, JobSeeker.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Error processing application.'})
