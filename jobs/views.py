from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import Job, JobSeeker, Employer, Application
from .validators import DTIPermitValidator
import requests
import re
import json
import uuid
import secrets
import string
import time
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

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
        logger.error(f"reCAPTCHA verification error: {str(e)}")
        return False


def validate_password_complexity(password):
    """
    Validate password complexity requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long.')
    if not any(c.isupper() for c in password):
        errors.append('Password must contain at least one uppercase letter.')
    if not any(c.islower() for c in password):
        errors.append('Password must contain at least one lowercase letter.')
    if not any(c.isdigit() for c in password):
        errors.append('Password must contain at least one digit.')
    if not any(c in string.punctuation for c in password):
        errors.append('Password must contain at least one special character (!@#$%^&*).')
    
    return errors


def generate_secure_reset_code():
    """Generate a secure alphanumeric password reset code (8 characters)"""
    # Use alphanumeric characters (no easily confused characters like 0/O, 1/l/I)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    code = ''.join(secrets.choice(chars) for _ in range(8))
    return code


def generate_secure_username():
    """Generate a secure username using UUID to prevent enumeration"""
    # Use UUID4 truncated for privacy and security
    return 'user_' + str(uuid.uuid4())[:12]


def is_password_reset_rate_limited(request):
    """Check if user has exceeded password reset attempts (max 3 per 15 minutes)"""
    session_key = 'password_reset_attempts'
    attempts = request.session.get(session_key, {})
    current_time = time.time()
    
    # Clean old attempts older than 15 minutes
    attempts = {
        addr: times for addr, times in attempts.items()
        if any(t > current_time - (15 * 60) for t in times)
    }
    
    client_ip = get_client_ip(request)
    ip_attempts = attempts.get(client_ip, [])
    ip_attempts = [t for t in ip_attempts if t > current_time - (15 * 60)]
    
    if len(ip_attempts) >= 3:
        return True
    
    ip_attempts.append(current_time)
    attempts[client_ip] = ip_attempts
    request.session[session_key] = attempts
    
    return False


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
        logger.error(f"Email Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
    @method_decorator(never_cache)
    def post(self, request):
        from axes.models import AccessAttempt
        from django.utils import timezone
        from datetime import timedelta
        
        login_input = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        
        # Check if user is already locked out by checking AccessAttempt model
        client_ip = get_client_ip(request)
        try:
            access_attempt = AccessAttempt.objects.get(ip_address=client_ip)
            if access_attempt.failures_since_start >= 5:
                # Check if lockout period has expired
                cooloff_until = access_attempt.attempt_time + timedelta(seconds=600)  # 10 minutes
                if timezone.now() < cooloff_until:
                    messages.error(request, 'Account locked due to too many failed attempts. Try again in 10 minutes or use Forgot Password.')
                    return redirect('/auth/?locked=true')
        except AccessAttempt.DoesNotExist:
            pass
        
        # Verify CAPTCHA (always enforced - no DEBUG bypass)
        if not recaptcha_token:
            messages.error(request, 'Please verify that you are not a robot.')
            return redirect('auth')
        
        if not verify_recaptcha(recaptcha_token):
            messages.error(request, 'CAPTCHA verification failed. Please try again.')
            return redirect('auth')
        
        # Try to authenticate with email first, then username
        # django-axes middleware will automatically track failed attempts
        user = None
        try:
            user_obj = User.objects.get(email=login_input)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            # Try with username if email doesn't exist
            user = authenticate(request, username=login_input, password=password)
        
        if user is not None:
            # Check if account is still active
            if not user.is_active:
                messages.error(request, 'Your account has not been activated yet. Please check your email for verification link.')
                return redirect('auth')
            
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
            # django-axes will automatically handle rate limiting via middleware
            # Calculate remaining attempts
            attempts = AccessAttempt.objects.filter(
                ip_address=client_ip,
                attempt_time__gte=timezone.now() - timedelta(minutes=15)
            )
            
            failures = attempts.aggregate(Sum('failures_since_start'))['failures_since_start__sum'] or 0
            remaining = max(0, 5 - failures)
            
            if remaining > 0:
                messages.error(request, f'Invalid credentials. {remaining} attempt{"s" if remaining != 1 else ""} remaining.')
            else:
                messages.error(request, 'Account locked due to too many failed attempts. Try again in 10 minutes or use Forgot Password.')
        
        return redirect('auth')

class RegisterJobSeekerView(View):
    @method_decorator(never_cache)
    def post(self, request):
        full_name = request.POST.get('fullName', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        province = request.POST.get('province', '').strip()
        skills = request.POST.get('skills', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        
        # ALWAYS verify CAPTCHA (removed DEBUG check for security)
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
        
        # Check password complexity (minimum 8 chars with complexity)
        complexity_errors = validate_password_complexity(password)
        if complexity_errors:
            for error in complexity_errors:
                messages.error(request, error)
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login or use a different email.')
            return redirect('register')
        
        try:
            # Create user with secure username (removed predictable pattern)
            username = generate_secure_username()
            # Ensure uniqueness
            while User.objects.filter(username=username).exists():
                username = generate_secure_username()
            
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else 'User'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Inactive until email verified
            )
            
            # Create job seeker profile
            JobSeeker.objects.create(
                user=user,
                mobile=phone,
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
    @method_decorator(never_cache)
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
        dti_permit = request.FILES.get('dtiPermit')
        
        # ALWAYS verify CAPTCHA (removed DEBUG check for security)
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
        
        # Check password complexity (minimum 8 chars with complexity)
        complexity_errors = validate_password_complexity(password)
        if complexity_errors:
            for error in complexity_errors:
                messages.error(request, error)
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login or use a different email.')
            return redirect('register')
        
        if not dti_permit:
            messages.error(request, 'Please upload your DTI permit.')
            return redirect('register')
        
        # Validate DTI permit file
        try:
            DTIPermitValidator.validate(dti_permit)
        except ValidationError as e:
            messages.error(request, f'DTI permit validation failed: {str(e)}')
            logger.warning(f"DTI permit validation failed for {email}: {str(e)}")
            return redirect('register')
        
        try:
            # Create user with secure username (removed predictable pattern)
            username = generate_secure_username()
            # Ensure uniqueness
            while User.objects.filter(username=username).exists():
                username = generate_secure_username()
            
            name_parts = contact_person.split()
            first_name = name_parts[0] if name_parts else 'User'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Inactive until admin approves DTI permit
            )
            
            # Create employer profile with DTI permit
            Employer.objects.create(
                user=user,
                business_name=business_name,
                contact_number=phone,
                province=province,
                business_description=business_description,
                dti_permit=dti_permit
            )
            
            messages.success(request, 'Registration successful! Admin will review your DTI permit and activate your account shortly. Please check your email for updates.')
            
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'Registration failed. Please try again. {str(e)}')
            return redirect('register')
            name_parts = contact_person.split()
            first_name = name_parts[0] if name_parts else 'User'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Inactive until admin approves DTI permit
            )
            
            # Create employer profile with DTI permit
            Employer.objects.create(
                user=user,
                business_name=business_name,
                contact_number=phone,
                province=province,
                business_description=business_description,
                dti_permit=dti_permit
            )
            
            messages.success(request, 'Registration successful! Admin will review your DTI permit and activate your account shortly. Please check your email for updates.')
            
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'Registration failed. Please try again. {str(e)}')
            return redirect('register')

class LogoutView(View):
    def get(self, request):
        # Explicitly invalidate session for security
        if request.user.is_authenticated:
            request.session.flush()  # Clear all session data
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('index')
    
    def post(self, request):
        # Explicitly invalidate session for security
        if request.user.is_authenticated:
            request.session.flush()  # Clear all session data
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('index')

class JobListView(View):
    def get(self, request):
        # Only show approved and active jobs in public listings
        jobs = Job.objects.filter(is_active=True, is_approved=True)
        province_filter = request.GET.get('province', '')
        category_filter = request.GET.get('category', '')
        search_query = request.GET.get('q', '')
        
        if province_filter:
            jobs = jobs.filter(province=province_filter)
        if category_filter:
            jobs = jobs.filter(category=category_filter)
        if search_query:
            jobs = jobs.filter(location__icontains=search_query) | jobs.filter(province__icontains=search_query)
        
        # Check if user is a job seeker and has incomplete profile
        profile_complete = True
        if request.user.is_authenticated:
            try:
                job_seeker = JobSeeker.objects.get(user=request.user)
                profile_complete = is_profile_complete(job_seeker)
                if not profile_complete:
                    messages.warning(request, 'Please complete your profile to apply for jobs.')
            except JobSeeker.DoesNotExist:
                pass
        
        return render(request, 'job_list.html', {'jobs': jobs, 'profile_complete': profile_complete})

def is_profile_complete(job_seeker):
    """Check if job seeker profile is complete"""
    required_fields = [
        job_seeker.mobile,
        job_seeker.barangay,
    ]
    
    # Check user fields
    if not job_seeker.user.first_name or not job_seeker.user.last_name:
        return False
    
    # Check all required job seeker fields
    return all(required_fields)


def get_ai_recommended_jobs(job_seeker, all_jobs, limit=5):
    """
    Use Google Gemini AI to recommend jobs based on job seeker's skills
    """
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return []
    
    try:
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Prepare job seeker info
        seeker_skills = job_seeker.skills if job_seeker.skills else "Not specified"
        seeker_info = f"Job Seeker Skills: {seeker_skills}"
        
        # Prepare available jobs info
        jobs_info = "\n".join([
            f"- Job ID {job.id}: {job.title} at {job.company.businessName if job.company else 'Unknown'} (Requirements: {job.required_skills if job.required_skills else 'Not specified'})"
            for job in all_jobs[:20]  # Limit to 20 jobs for context
        ])
        
        # Create prompt for Gemini
        prompt = f"""You are a job recommendation AI assistant. Based on the job seeker's skills, recommend the best matching jobs.

{seeker_info}

Available Jobs:
{jobs_info}

Please recommend the top {limit} jobs that best match the job seeker's skills. 
Return ONLY a JSON array with job IDs in this format:
{{"job_ids": [id1, id2, id3, ...]}}

Consider skill match, job requirements, and career fit."""

        # Call Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        result = json.loads(json_str)
        job_ids = result.get("job_ids", [])
        
        # Filter recommended jobs
        recommended_jobs = [job for job in all_jobs if job.id in job_ids]
        
        return recommended_jobs[:limit]
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return []


@method_decorator(login_required, name='dispatch')
class ApplyJobView(View):
    def get(self, request, job_id):
        """Handle GET request - check profile and redirect if incomplete"""
        try:
            job_seeker = JobSeeker.objects.get(user=request.user)
            
            # Check if profile is complete
            if not is_profile_complete(job_seeker):
                messages.warning(request, 'Please complete your profile before applying for jobs.')
                return redirect('edit_profile')
            
            # Profile is complete, process the application
            job = Job.objects.get(id=job_id)
            application, created = Application.objects.get_or_create(
                job_seeker=job_seeker,
                job=job
            )
            
            if created:
                messages.success(request, 'Application submitted successfully!')
            else:
                messages.warning(request, 'You have already applied for this job.')
            
            return redirect('job_list')
        except JobSeeker.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('edit_profile')
        except Job.DoesNotExist:
            messages.error(request, 'Job not found.')
            return redirect('job_list')
    
    def post(self, request, job_id):
        """Handle POST request - for AJAX submissions"""
        try:
            job = Job.objects.get(id=job_id)
            job_seeker = JobSeeker.objects.get(user=request.user)
            
            # Check if profile is complete
            if not is_profile_complete(job_seeker):
                return JsonResponse({
                    'success': False, 
                    'message': 'Please complete your profile before applying for jobs.',
                    'redirect': True,
                    'redirect_url': request.build_absolute_uri('/edit-profile/')
                })
            
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


@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    """Edit job seeker profile"""
    def get(self, request):
        try:
            job_seeker = JobSeeker.objects.get(user=request.user)
        except JobSeeker.DoesNotExist:
            messages.error(request, 'Please complete your job seeker profile first.')
            return redirect('seeker_dashboard')
        
        context = {'job_seeker': job_seeker}
        return render(request, 'edit_profile.html', context)
    
    def post(self, request):
        try:
            user = request.user
            job_seeker = JobSeeker.objects.get(user=request.user)
            
            # Update user fields
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip().lower()
            user.save()
            
            # Update job seeker fields
            job_seeker.mobile = request.POST.get('mobile', '').strip()
            job_seeker.province = request.POST.get('province', '').strip()
            job_seeker.municipality = request.POST.get('municipality', '').strip()
            job_seeker.barangay = request.POST.get('barangay', '').strip()
            job_seeker.skills = request.POST.get('skills', '').strip()
            
            job_seeker.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('seeker_dashboard')
            
        except JobSeeker.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('seeker_dashboard')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('edit_profile')


class ForgotPasswordView(View):
    """Handle forgot password request with rate limiting (max 3 per 15 minutes)"""
    @method_decorator(never_cache)
    def get(self, request):
        return render(request, 'forgot_password.html')
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        
        if not email:
            return render(request, 'forgot_password.html', {'error': 'Please enter your email.'})
        
        # Check rate limiting (max 3 attempts per 15 minutes per IP)
        if is_password_reset_rate_limited(request):
            messages.error(request, 'Too many password reset attempts. Please try again in 15 minutes.')
            return render(request, 'forgot_password.html', {'error': 'Rate limit exceeded'})
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, 'If an account exists with this email, you will receive a verification code shortly.')
            return render(request, 'forgot_password.html')
        
        # Generate secure alphanumeric code (8 characters, no confusing chars)
        verification_code = generate_secure_reset_code()
        
        # Store code in session with expiration time (15 minutes)
        request.session['reset_email'] = email
        request.session['reset_code'] = verification_code
        request.session['code_expiration'] = time.time() + (15 * 60)  # 15 minutes from now
        
        # Send email with code
        try:
            send_mail(
                'TrabahoPH - Password Reset Code',
                f'Your password reset code is: {verification_code}\n\nThis code expires in 15 minutes.\n\nIf you did not request this, please ignore this email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Verification code sent to your email!')
            return redirect('verify_code')
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            messages.error(request, 'Error sending verification code. Please try again.')
            return render(request, 'forgot_password.html', {'error': str(e)})


class VerifyCodeView(View):
    """Verify the reset code"""
    def get(self, request):
        # Check if user has started the reset process
        if 'reset_email' not in request.session:
            return redirect('forgot_password')
        
        # Check if code has expired
        import time
        if time.time() > request.session.get('code_expiration', 0):
            messages.error(request, 'Your verification code has expired. Please request a new one.')
            return redirect('forgot_password')
        
        # Calculate remaining time
        remaining_time = int(request.session.get('code_expiration', 0) - time.time())
        
        return render(request, 'verify_code.html', {'expiration_time': remaining_time})
    
    def post(self, request):
        # Check session
        if 'reset_email' not in request.session or 'reset_code' not in request.session:
            return redirect('forgot_password')
        
        # Check expiration
        import time
        if time.time() > request.session.get('code_expiration', 0):
            del request.session['reset_email']
            del request.session['reset_code']
            del request.session['code_expiration']
            messages.error(request, 'Your verification code has expired. Please request a new one.')
            return redirect('forgot_password')
        
        entered_code = request.POST.get('code', '').strip()
        stored_code = request.session.get('reset_code', '')
        
        if entered_code != stored_code:
            messages.error(request, 'Invalid verification code. Please try again.')
            remaining_time = int(request.session.get('code_expiration', 0) - time.time())
            return render(request, 'verify_code.html', {'expiration_time': remaining_time})
        
        # Code verified, mark as verified in session
        request.session['code_verified'] = True
        messages.success(request, 'Code verified! Please set your new password.')
        return redirect('reset_password')


class ResendCodeView(View):
    """Resend verification code"""
    def post(self, request):
        if 'reset_email' not in request.session:
            return redirect('forgot_password')
        
        email = request.session.get('reset_email')
        
        # Generate new secure alphanumeric code (not 6-digit)
        verification_code = generate_secure_reset_code()
        
        # Update session
        request.session['reset_code'] = verification_code
        request.session['code_expiration'] = time.time() + (15 * 60)
        
        # Send email
        try:
            send_mail(
                'TrabahoPH - Password Reset Code',
                f'Your new password reset code is: {verification_code}\n\nThis code expires in 15 minutes.\n\nIf you did not request this, please ignore this email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'New verification code sent to your email!')
        except Exception as e:
            messages.error(request, 'Error sending verification code. Please try again.')
        
        remaining_time = int(request.session.get('code_expiration', 0) - time.time())
        return render(request, 'verify_code.html', {'expiration_time': remaining_time})


class ResetPasswordView(View):
    """Reset password with complexity requirements"""
    @method_decorator(never_cache)
    def get(self, request):
        # Check if code has been verified
        if 'code_verified' not in request.session or not request.session['code_verified']:
            return redirect('forgot_password')
        
        return render(request, 'reset_password.html')
    
    def post(self, request):
        # Check verification
        if 'code_verified' not in request.session or not request.session['code_verified']:
            return redirect('forgot_password')
        
        email = request.session.get('reset_email')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validate passwords
        if not password:
            return render(request, 'reset_password.html', {'error': 'Password is required.'})
        
        if password != confirm_password:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match.'})
        
        # Check password complexity (8 chars minimum with uppercase, lowercase, number, special char)
        complexity_errors = validate_password_complexity(password)
        if complexity_errors:
            error_msg = ' '.join(complexity_errors)
            return render(request, 'reset_password.html', {'error': error_msg})
        
        # Update password
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # Clear session data
            del request.session['reset_email']
            del request.session['reset_code']
            del request.session['code_expiration']
            del request.session['code_verified']
            
            # Clear any password reset attempts after successful reset
            if 'password_reset_attempts' in request.session:
                del request.session['password_reset_attempts']
            
            messages.success(request, 'Password reset successfully! Please log in with your new password.')
            return redirect('auth')
        except User.DoesNotExist:
            return render(request, 'reset_password.html', {'error': 'User not found.'})
        except Exception as e:
            return render(request, 'reset_password.html', {'error': f'Error resetting password: {str(e)}'})
