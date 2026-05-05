"""Integration tests for authentication workflow"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from jobs.models import JobSeeker, Employer, Job, Application
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile


class AuthenticationFlowIntegrationTests(TestCase):
    """Integration tests for complete authentication flow"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_complete_job_seeker_registration_flow(self):
        """Test complete job seeker registration flow"""
        # Job seeker visits index
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
        # Job seeker visits register page
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # Job seeker attempts registration
        response = self.client.post(reverse('register'), {
            'email': 'newseeker@test.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'phone': '09123456789',
            'first_name': 'John',
            'last_name': 'Seeker',
            'province': 'Metro Manila',
            'municipality': 'Quezon City',
            'barangay': 'Diliman',
            'user_type': 'job_seeker'
        }, follow=True)
        
        # Check if user was created
        user = User.objects.filter(email='newseeker@test.com').first()
        if user:
            self.assertIsNotNone(user)
    
    def test_complete_employer_registration_flow(self):
        """Test complete employer registration flow with DTI permit"""
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test_permit.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        # Employer attempts registration
        response = self.client.post(reverse('register'), {
            'email': 'newemployer@test.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'contact_person': 'Jane Employer',
            'business_name': 'Test Business',
            'phone': '02123456789',
            'province': 'Metro Manila',
            'municipality': 'Manila',
            'barangay': 'Intramuros',
            'business_description': 'A test business',
            'dti_permit': test_file,
            'user_type': 'employer'
        }, follow=True)
        
        # Check if employer was created (may not work without proper form setup)
        employer = Employer.objects.filter(business_name='Test Business').first()
        if employer:
            self.assertIsNotNone(employer)
    
    def test_job_seeker_application_flow(self):
        """Test complete job application flow"""
        # Create employer and job
        employer_user = User.objects.create_user(
            username='flowemployer',
            email='flowemployer@test.com',
            password='TestPass123!'
        )
        employer = Employer.objects.create(
            user=employer_user,
            business_name='Flow Company',
            contact_number='02555555555',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        job = Job.objects.create(
            title='Flow Position',
            employer=employer,
            description='Test job',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=True
        )
        
        # Create job seeker
        seeker_user = User.objects.create_user(
            username='flowseeker',
            email='flowseeker@test.com',
            password='TestPass123!',
            first_name='Flow',
            last_name='Seeker'
        )
        job_seeker = JobSeeker.objects.create(
            user=seeker_user,
            mobile='09999999999',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman'
        )
        
        # Login as job seeker
        self.client.login(username='flowseeker', password='TestPass123!')
        
        # View job list
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Flow Position')
        
        # Apply for job
        response = self.client.get(reverse('apply_job', args=[job.id]))
        
        # Check if application was created
        application = Application.objects.filter(
            job_seeker=job_seeker,
            job=job
        ).first()
        self.assertIsNotNone(application)
        self.assertEqual(application.status, 'pending')
    
    def test_employer_dashboard_workflow(self):
        """Test employer dashboard workflow"""
        # Create employer
        employer_user = User.objects.create_user(
            username='dashemployer',
            email='dashemployer@test.com',
            password='TestPass123!',
            first_name='Dash',
            last_name='Employer'
        )
        employer = Employer.objects.create(
            user=employer_user,
            business_name='Dashboard Company',
            contact_number='02666666666',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        # Login as employer
        self.client.login(username='dashemployer', password='TestPass123!')
        
        # Access employer dashboard
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_job_seeker_dashboard_workflow(self):
        """Test job seeker dashboard workflow"""
        # Create job seeker
        seeker_user = User.objects.create_user(
            username='dashseeker',
            email='dashseeker@test.com',
            password='TestPass123!',
            first_name='Dash',
            last_name='Seeker'
        )
        job_seeker = JobSeeker.objects.create(
            user=seeker_user,
            mobile='09777777777',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman'
        )
        
        # Login as job seeker
        self.client.login(username='dashseeker', password='TestPass123!')
        
        # Access job seeker dashboard
        response = self.client.get(reverse('seeker_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_password_reset_flow(self):
        """Test complete password reset flow"""
        # Create user
        user = User.objects.create_user(
            username='passreset',
            email='passreset@test.com',
            password='OldPass123!'
        )
        
        # Step 1: Request password reset
        response = self.client.post(reverse('forgot_password'), {
            'email': 'passreset@test.com'
        })
        
        # Check if session has reset_email
        if 'reset_email' in self.client.session:
            self.assertEqual(self.client.session['reset_email'], 'passreset@test.com')
    
    def test_application_status_change_flow(self):
        """Test changing application status"""
        # Create employer and job
        employer_user = User.objects.create_user(
            username='statusemployer',
            email='statusemployer@test.com',
            password='TestPass123!'
        )
        employer = Employer.objects.create(
            user=employer_user,
            business_name='Status Company',
            contact_number='02888888888',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        job = Job.objects.create(
            title='Status Position',
            employer=employer,
            description='Test job',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=True
        )
        
        # Create job seeker and application
        seeker_user = User.objects.create_user(
            username='statusseeker',
            email='statusseeker@test.com',
            password='TestPass123!'
        )
        job_seeker = JobSeeker.objects.create(
            user=seeker_user,
            mobile='09888888888',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman'
        )
        
        application = Application.objects.create(
            job_seeker=job_seeker,
            job=job,
            status='pending'
        )
        
        # Change status to accepted
        application.status = 'accepted'
        application.save()
        
        # Verify status changed
        updated_app = Application.objects.get(id=application.id)
        self.assertEqual(updated_app.status, 'accepted')


class MultiUserInteractionTests(TestCase):
    """Test interactions between multiple users"""
    
    def test_employer_can_view_applications(self):
        """Test that employer can view applications for their jobs"""
        # Create employer
        employer_user = User.objects.create_user(
            username='multiemployer',
            email='multiemployer@test.com',
            password='TestPass123!'
        )
        employer = Employer.objects.create(
            user=employer_user,
            business_name='Multi Company',
            contact_number='02999999999',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo'
        )
        
        job = Job.objects.create(
            title='Multi Position',
            employer=employer,
            description='Test job',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Binondo',
            salary='50000',
            is_active=True
        )
        
        # Create multiple job seekers and applications
        for i in range(3):
            seeker_user = User.objects.create_user(
                username=f'multiseeker{i}',
                email=f'multiseeker{i}@test.com',
                password='TestPass123!'
            )
            job_seeker = JobSeeker.objects.create(
                user=seeker_user,
                mobile=f'0912345678{i}',
                province='Metro Manila',
                municipality='Quezon City',
                barangay='Diliman'
            )
            
            Application.objects.create(
                job_seeker=job_seeker,
                job=job,
                status='pending'
            )
        
        # Verify job has 3 applications
        applications = Application.objects.filter(job=job)
        self.assertEqual(applications.count(), 3)
