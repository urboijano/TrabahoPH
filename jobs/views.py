from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from .models import Job, JobSeeker, Employer, Application
import requests
import re

def verify_recaptcha(token):
    """Verify reCAPTCHA v2 token with Google"""
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {str(e)}")
        return False


def is_valid_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def send_verification_email(user, request, user_type='seeker'):
    """Send email verification link to user"""
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Build verification link
        verification_link = request.build_absolute_uri(
            f'/verify-email/{uid}/{token}/'
        )
        
        subject = 'Verify Your Trabaho Email Address'
        message = f"""
        Hello {user.first_name or user.username},

        Thank you for registering with Trabaho! 

        Please click the link below to verify your email address:
        {verification_link}

        This link will expire in 1 hour.

        If you did not create this account, please ignore this email.

        Best regards,
        Trabaho Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False


class IndexView(View):
    def get(self, request):
        jobs = Job.objects.filter(is_active=True)[:6]
        
        # Get statistics from database
        active_jobs_count = Job.objects.filter(is_active=True).count()
        job_seekers_count = JobSeeker.objects.count()
        employers_count = Employer.objects.count()
        successful_hires_count = Application.objects.filter(status='accepted').count()
        
        context = {
            'jobs': jobs,
            'user': request.user,
            'is_authenticated': request.user.is_authenticated,
            'active_jobs_count': active_jobs_count,
            'job_seekers_count': job_seekers_count,
            'employers_count': employers_count,
            'successful_hires_count': successful_hires_count,
        }
        return render(request, 'index.html', context)

class AuthView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        context = {
            'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
        }
        return render(request, 'auth.html', context)

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        context = {'show_register': True, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}
        return render(request, 'register.html', context)

class LoginView(View):
    def post(self, request):
        login_input = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        
        # Verify CAPTCHA
        if not recaptcha_token:
            messages.error(request, 'Please verify that you are not a robot.')
            return redirect('auth')
        
        if not verify_recaptcha(recaptcha_token):
            messages.error(request, 'CAPTCHA verification failed. Please try again.')
            return redirect('auth')
        
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
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        
        # Verify CAPTCHA
        if not recaptcha_token:
            messages.error(request, 'Please verify that you are not a robot.')
            return redirect('register')
        
        if not verify_recaptcha(recaptcha_token):
            messages.error(request, 'CAPTCHA verification failed. Please try again.')
            return redirect('register')
        
        # Validation
        if not all([full_name, email, phone, province, password]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')
        
        # Validate email format
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address.')
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
            # Create user (inactive until email verified)
            username = email.split('@')[0] + str(User.objects.count())
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0] if full_name else 'User',
                is_active=False  # Inactive until email verified
            )
            
            # Create job seeker profile
            JobSeeker.objects.create(
                user=user,
                phone=phone,
                province=province,
                skills=skills
            )
            
            # Send verification email
            if send_verification_email(user, request, 'seeker'):
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
            else:
                messages.warning(request, 'Registration successful! However, verification email could not be sent. Please contact support.')
            
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
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        
        # Verify CAPTCHA
        if not recaptcha_token:
            messages.error(request, 'Please verify that you are not a robot.')
            return redirect('register')
        
        if not verify_recaptcha(recaptcha_token):
            messages.error(request, 'CAPTCHA verification failed. Please try again.')
            return redirect('register')
        
        # Validation
        if not all([business_name, contact_person, email, phone, province, password]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')
        
        # Validate email format
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address.')
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
            # Create user (inactive until email verified)
            username = business_name.replace(' ', '')[:15] + str(User.objects.count())
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=contact_person,
                is_active=False  # Inactive until email verified
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
            
            # Send verification email
            if send_verification_email(user, request, 'employer'):
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
            else:
                messages.warning(request, 'Registration successful! However, verification email could not be sent. Please contact support.')
            
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


class VerifyEmailView(View):
    """Handle email verification via token link"""
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            # Token is valid - activate user
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('auth')
        else:
            messages.error(request, 'Email verification link is invalid or has expired.')
            return redirect('register')
