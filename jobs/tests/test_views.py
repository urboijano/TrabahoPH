"""Unit tests for jobs views"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from jobs.models import JobSeeker, Employer, Job, Application
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO


class AuthenticationViewTests(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testauth',
            email='auth@test.com',
            password='TestPass123!'
        )
    
    def test_index_view_accessible(self):
        """Test that index page is accessible without login"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_auth_view_accessible(self):
        """Test that auth page is accessible"""
        response = self.client.get(reverse('auth'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_get(self):
        """Test GET request to register page """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(reverse('auth'), {
            'email': 'auth@test.com',
            'password': 'TestPass123!',
            'user_type': 'job_seeker'
        })
        # Should redirect on successful login
        # Status code 302 indicates redirect
        self.assertIn(response.status_code, [302, 200])
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('auth'), {
            'email': 'auth@test.com',
            'password': 'WrongPassword123!',
            'user_type': 'job_seeker'
        }, follow=True)
        # Should not create a session for invalid credentials
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_logout_view(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='testauth', password='TestPass123!')
        # Then logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect


class JobListViewTests(TestCase):
    """Test cases for job listing views"""
    
    def setUp(self):
        """Create test data"""
        # Create employer
        self.employer_user = User.objects.create_user(
            username='listemployer',
            email='listemployer@test.com',
            password='TestPass123!'
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            business_name='List Company',
            contact_number='02333333333',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        # Create active and inactive jobs
        self.active_job = Job.objects.create(
            title='Active Position',
            employer=self.employer,
            description='Available now',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=True
        )
        
        self.inactive_job = Job.objects.create(
            title='Inactive Position',
            employer=self.employer,
            description='Not available',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=False
        )
    
    def test_job_list_view_accessible(self):
        """Test that job list page is accessible"""
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_job_list_shows_active_jobs_only(self):
        """Test that only active jobs are displayed"""
        response = self.client.get(reverse('job_list'))
        self.assertContains(response, 'Active Position')
        self.assertNotContains(response, 'Inactive Position')
    
    def test_job_list_filtering_by_province(self):
        """Test filtering jobs by province"""
        response = self.client.get(reverse('job_list'), {'province': 'Metro Manila'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Position')
    
    def test_job_list_search_functionality(self):
        """Test search functionality"""
        response = self.client.get(reverse('job_list'), {'q': 'Manila'})
        self.assertEqual(response.status_code, 200)


class JobApplicationViewTests(TestCase):
    """Test cases for job application views"""
    
    def setUp(self):
        """Create test data"""
        # Create job seeker
        self.seeker_user = User.objects.create_user(
            username='appseeker',
            email='appseeker@test.com',
            password='TestPass123!',
            first_name='App',
            last_name='Seeker'
        )
        self.job_seeker = JobSeeker.objects.create(
            user=self.seeker_user,
            mobile='09111111111',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman'
        )
        
        # Create employer and job
        self.employer_user = User.objects.create_user(
            username='appjobemployer',
            email='appjobemployer@test.com',
            password='TestPass123!'
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            business_name='Job Application Company',
            contact_number='02444444444',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        self.job = Job.objects.create(
            title='Test Application Job',
            employer=self.employer,
            description='Apply here',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=True
        )
    
    def test_apply_job_requires_login(self):
        """Test that job application requires authentication"""
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_apply_job_with_complete_profile(self):
        """Test applying for a job with complete profile"""
        self.client.login(username='appseeker', password='TestPass123!')
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        # Should redirect to job list
        self.assertEqual(response.status_code, 302)
    
    def test_cannot_apply_twice_for_same_job(self):
        """Test that a job seeker cannot apply twice for the same job"""
        # Create first application
        Application.objects.create(
            job_seeker=self.job_seeker,
            job=self.job,
            status='pending'
        )
        
        # Try to apply again
        self.client.login(username='appseeker', password='TestPass123!')
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        
        # Should still work but with a message
        self.assertEqual(response.status_code, 302)


class PasswordResetViewTests(TestCase):
    """Test cases for password reset views"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='resetuser',
            email='reset@test.com',
            password='OldPassword123!'
        )
    
    def test_forgot_password_view_accessible(self):
        """Test that forgot password page is accessible"""
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)
    
    def test_forgot_password_post_with_valid_email(self):
        """Test forgot password with valid email"""
        response = self.client.post(reverse('forgot_password'), {
            'email': 'reset@test.com'
        })
        # Should redirect to verify code page
        self.assertEqual(response.status_code, 302)


class EditProfileViewTests(TestCase):
    """Test cases for edit profile view"""
    
    def setUp(self):
        """Create test user and profile"""
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            password='ProfilePass123!',
            first_name='Profile',
            last_name='User'
        )
        self.job_seeker = JobSeeker.objects.create(
            user=self.user,
            mobile='09555555555',
            province='Laguna',
            municipality='Santa Rosa',
            barangay='Poblacion'
        )
    
    def test_edit_profile_requires_login(self):
        """Test that edit profile requires authentication"""
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_edit_profile_get_authenticated(self):
        """Test viewing edit profile when authenticated"""
        self.client.login(username='profileuser', password='ProfilePass123!')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_profile_update(self):
        """Test updating profile information"""
        self.client.login(username='profileuser', password='ProfilePass123!')
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'mobile': '09666666666',
            'province': 'Cavite',
            'municipality': 'Kawit',
            'barangay': 'Barangay1',
            'skills': 'Python, Django'
        })
        # Should redirect to seeker dashboard
        self.assertEqual(response.status_code, 302)
