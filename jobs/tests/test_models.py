"""Unit tests for jobs models"""

from django.test import TestCase
from django.contrib.auth.models import User
from jobs.models import JobSeeker, Employer, Job, Application
from django.core.exceptions import ValidationError
from django.utils import timezone


class JobSeekerModelTests(TestCase):
    """Test cases for JobSeeker model"""
    
    def setUp(self):
        """Create a test user and job seeker"""
        self.user = User.objects.create_user(
            username='testseeker',
            email='seeker@test.com',
            password='TestPass123!',
            first_name='John',
            last_name='Seeker'
        )
        self.job_seeker = JobSeeker.objects.create(
            user=self.user,
            mobile='09123456789',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman',
            skills='Python, Django, REST API'
        )
    
    def test_job_seeker_creation(self):
        """Test that JobSeeker is created successfully"""
        self.assertEqual(self.job_seeker.user.username, 'testseeker')
        self.assertEqual(self.job_seeker.mobile, '09123456789')
        self.assertEqual(self.job_seeker.province, 'Metro Manila')
    
    def test_job_seeker_string_representation(self):
        """Test the __str__ method"""
        expected_str = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(str(self.job_seeker), expected_str)
    
    def test_job_seeker_one_to_one_relationship(self):
        """Test that only one JobSeeker can be associated with a User"""
        with self.assertRaises(Exception):
            JobSeeker.objects.create(
                user=self.user,  # Same user
                mobile='09987654321',
                province='Cavite',
                municipality='Kawit',
                barangay='Test'
            )
    
    def test_job_seeker_fields(self):
        """Test all fields of JobSeeker"""
        self.assertIsNotNone(self.job_seeker.created_at)
        self.assertTrue(len(self.job_seeker.mobile) > 0)
        self.assertTrue(len(self.job_seeker.skills) > 0)


class EmployerModelTests(TestCase):
    """Test cases for Employer model"""
    
    def setUp(self):
        """Create a test user and employer"""
        self.user = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='TestPass123!',
            first_name='Jane',
            last_name='Employer'
        )
        self.employer = Employer.objects.create(
            user=self.user,
            business_name='Tech Company',
            contact_number='02123456789',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Intramuros',
            business_description='A leading tech company'
        )
    
    def test_employer_creation(self):
        """Test that Employer is created successfully"""
        self.assertEqual(self.employer.business_name, 'Tech Company')
        self.assertEqual(self.employer.business_type, 'IT')
        self.assertIsNone(self.employer.dti_permit)  # Should be None initially
    
    def test_employer_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.employer), 'Tech Company')
    
    def test_employer_fields(self):
        """Test all required fields are present"""
        self.assertIsNotNone(self.employer.created_at)
        self.assertTrue(len(self.employer.business_description) > 0)


class JobModelTests(TestCase):
    """Test cases for Job model"""
    
    def setUp(self):
        """Create test data"""
        # Create employer and job
        self.employer_user = User.objects.create_user(
            username='jobemployer',
            email='jobemployer@test.com',
            password='TestPass123!'
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            business_name='Job Company',
            contact_number='02111111111',
            business_type='Manufacturing',
            province='Cebu',
            municipality='Cebu City',
            barangay='Mabolo'
        )
        
        self.job = Job.objects.create(
            title='Senior Developer',
            employer=self.employer,
            description='Looking for a senior developer',
            category='Manufacturing',
            location='Cebu City',
            province='Cebu',
            municipality='Cebu City',
            barangay='Mabolo',
            salary='50000-60000',
            is_active=True
        )
    
    def test_job_creation(self):
        """Test that Job is created successfully"""
        self.assertEqual(self.job.title, 'Senior Developer')
        self.assertTrue(self.job.is_active)
        self.assertIsNotNone(self.job.created_at)
    
    def test_job_foreign_key_relationship(self):
        """Test the ForeignKey relationship with Employer"""
        self.assertEqual(self.job.employer, self.employer)
    
    def test_job_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.job), 'Senior Developer')
    
    def test_job_category_choices(self):
        """Test that job category is from valid choices"""
        valid_categories = ['Agriculture', 'Tourism', 'Manufacturing', 'Government', 
                          'Healthcare', 'Education', 'Retail', 'Construction', 'Other']
        self.assertIn(self.job.category, valid_categories)
    
    def test_job_is_active_toggle(self):
        """Test toggling job active status"""
        self.assertTrue(self.job.is_active)
        self.job.is_active = False
        self.job.save()
        self.assertFalse(self.job.is_active)
    
    def test_job_updated_at_field(self):
        """Test that updated_at changes when job is modified"""
        original_updated = self.job.updated_at
        self.job.title = 'Lead Developer'
        self.job.save()
        self.assertGreater(self.job.updated_at, original_updated)


class ApplicationModelTests(TestCase):
    """Test cases for Application model"""
    
    def setUp(self):
        """Create test data"""
        # Create job seeker
        self.seeker_user = User.objects.create_user(
            username='testapplicant',
            email='applicant@test.com',
            password='TestPass123!'
        )
        self.job_seeker = JobSeeker.objects.create(
            user=self.seeker_user,
            mobile='09123456789',
            province='Metro Manila',
            municipality='Quezon City',
            barangay='Diliman'
        )
        
        # Create employer and job
        self.employer_user = User.objects.create_user(
            username='appemployer',
            email='appemployer@test.com',
            password='TestPass123!'
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            business_name='App Company',
            contact_number='02222222222',
            business_type='IT',
            province='Metro Manila',
            municipality='Manila',
            barangay='Intramuros'
        )
        
        self.job = Job.objects.create(
            title='Developer',
            employer=self.employer,
            description='Developer needed',
            category='IT',
            location='Manila',
            province='Metro Manila',
            municipality='Manila',
            barangay='Intramuros',
            salary='40000-50000'
        )
        
        self.application = Application.objects.create(
            job_seeker=self.job_seeker,
            job=self.job,
            status='pending'
        )
    
    def test_application_creation(self):
        """Test that Application is created successfully"""
        self.assertEqual(self.application.status, 'pending')
        self.assertIsNotNone(self.application.applied_at)
    
    def test_application_string_representation(self):
        """Test the __str__ method"""
        expected = f"{self.job_seeker} - {self.job}"
        self.assertEqual(str(self.application), expected)
    
    def test_application_status_choices(self):
        """Test valid application status values"""
        valid_statuses = ['pending', 'accepted', 'rejected']
        self.assertIn(self.application.status, valid_statuses)
    
    def test_application_status_update(self):
        """Test updating application status"""
        self.application.status = 'accepted'
        self.application.save()
        self.assertEqual(self.application.status, 'accepted')
    
    def test_application_unique_together_constraint(self):
        """Test that a job seeker can only apply once per job"""
        with self.assertRaises(Exception):
            Application.objects.create(
                job_seeker=self.job_seeker,
                job=self.job,
                status='pending'
            )
    
    def test_application_relationships(self):
        """Test ForeignKey relationships"""
        self.assertEqual(self.application.job_seeker, self.job_seeker)
        self.assertEqual(self.application.job, self.job)
    
    def test_application_cascade_delete(self):
        """Test that deleting job seeker deletes their applications"""
        app_id = self.application.id
        self.job_seeker.delete()
        with self.assertRaises(Application.DoesNotExist):
            Application.objects.get(id=app_id)
