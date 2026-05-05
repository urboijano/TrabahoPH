# TrabahoPH Development Guidelines

## 🏗️ Project Structure

```
TrabahoPH/
├── jobs/                          # Main Django app
│   ├── migrations/                # Database migrations
│   ├── static/                    # Static files (CSS, JS)
│   ├── templates/                 # HTML templates
│   ├── tests/                     # Test suite
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_integration.py
│   ├── admin.py                   # Django admin configuration
│   ├── models.py                  # Data models
│   ├── views.py                   # View logic
│   ├── api_views.py               # REST API views
│   ├── serializers.py             # DRF serializers
│   ├── validators.py              # Custom validators
│   ├── signals.py                 # Django signals
│   ├── error_handlers.py          # Error handling
│   ├── apps.py                    # App configuration
│   └── urls.py                    # URL routing
├── trabaho/                       # Project settings
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Project URLs
│   └── wsgi.py                    # WSGI configuration
├── logs/                          # Application logs
├── media/                         # User uploads
├── manage.py                      # Django CLI
├── requirements.txt               # Python dependencies
└── .env                           # Environment variables
```

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create a new branch
git checkout -b feature/my-feature

# Make changes following guidelines below
# Commit with descriptive messages
git commit -m "feat: Add feature description"

# Push and create pull request
git push origin feature/my-feature
```

### 2. Running Tests
```bash
# Run all tests
python manage.py test jobs.tests

# Run specific test
python manage.py test jobs.tests.test_models.JobModelTests

# Run with verbosity
python manage.py test jobs.tests -v 2

# Generate coverage report
coverage run --source='jobs' manage.py test jobs.tests
coverage report
```

### 3. Database Changes
```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 📝 Coding Standards

### Python Style (PEP 8)
```python
# ✓ Good
class JobSeeker(models.Model):
    """Represents a job seeker in the system."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=11)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# ✗ Bad
class JobSeeker(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):return f"{self.user.first_name} {self.user.last_name}"
```

### Imports Organization
```python
# ✓ Good - Organized by category
# Standard library
import logging
from datetime import datetime

# Third-party
from django.db import models
from rest_framework import serializers

# Local
from .models import Job
from .validators import validate_file

# ✗ Bad - Random order
from django.db import models
import logging
from .validators import validate_file
from rest_framework import serializers
from datetime import datetime
from .models import Job
```

### Docstrings
```python
# ✓ Good
def validate_dti_permit(file_obj):
    """
    Validate DTI permit file.
    
    Args:
        file_obj: The file object to validate
        
    Returns:
        None
        
    Raises:
        ValidationError: If file doesn't meet requirements
    """
    pass

# ✗ Bad
def validate_dti_permit(file_obj):
    # validate file
    pass
```

### Logging
```python
# ✓ Good
logger.info(f"User {user.username} logged in successfully")
logger.error(f"Failed to send email to {email}: {str(e)}")
logger.warning(f"DTI permit validation failed for {business_name}")

# ✗ Bad
print(f"Logging in {user}")
print("Error!")
```

## 🧪 Testing Guidelines

### Test Structure
```python
from django.test import TestCase

class JobModelTests(TestCase):
    """Test cases for Job model"""
    
    def setUp(self):
        """Set up test data"""
        self.job = Job.objects.create(
            title='Test Job',
            ...
        )
    
    def test_job_creation(self):
        """Test that Job is created successfully"""
        self.assertEqual(self.job.title, 'Test Job')
    
    def test_job_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.job), 'Test Job')
```

### Coverage Requirements
- Models: 100% coverage
- Views: 80%+ coverage
- Utils: 95%+ coverage

### Test Naming Convention
```python
# Method names should be descriptive
test_job_creation()
test_job_creation_with_invalid_data()
test_employer_cannot_view_others_applications()
test_email_sent_on_application_accepted()
```

## 🔒 Security Best Practices

### 1. Input Validation
```python
# ✓ Good - Always validate
from .validators import ValidateDTIPermit

permit = request.FILES.get('dti_permit')
try:
    ValidateDTIPermit.validate(permit)
except ValidationError as e:
    return error_response(str(e))

# ✗ Bad - No validation
permit = request.FILES.get('dti_permit')
employer.dti_permit = permit
employer.save()
```

### 2. Sensitive Data
```python
# ✓ Good - Use environment variables
EMAIL_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# ✗ Bad - Hardcoded in code
EMAIL_PASSWORD = 'MySecurePassword123'
```

### 3. Password Security
```python
# ✓ Good - Use Django's password setting
user.set_password(password)
user.save()

# ✗ Bad - Plain text
user.password = password
user.save()
```

### 4. SQL Injection Prevention
```python
# ✓ Good - Use ORM
jobs = Job.objects.filter(province=province)

# ✗ Bad - Raw SQL
jobs = Job.objects.raw(f"SELECT * FROM jobs WHERE province = {province}")
```

## 🚨 Common Patterns & Anti-patterns

### Model Methods
```python
# ✓ Good - Business logic in model
class Application(models.Model):
    def mark_as_accepted(self):
        """Mark application as accepted and send notification"""
        self.status = 'accepted'
        self.save()
        # Send email notification
        notify_applicant(self)

# ✗ Bad - Logic scattered everywhere
# In view:
app = Application.objects.get(id=id)
app.status = 'accepted'
app.save()
# In another view:
app = Application.objects.get(id=id)
app.status = 'accepted'
app.save()
```

### Exception Handling
```python
# ✓ Good - Specific exceptions
try:
    job_seeker = JobSeeker.objects.get(user=user)
except JobSeeker.DoesNotExist:
    return error_response("Profile not found")

# ✗ Bad - Generic exception
try:
    job_seeker = JobSeeker.objects.get(user=user)
except Exception:
    return error_response("Error")
```

### Database Queries
```python
# ✓ Good - Efficient queries
jobs = Job.objects.filter(
    is_active=True,
    is_approved=True
).select_related('employer')

# ✗ Bad - N+1 query problem
jobs = Job.objects.filter(is_active=True, is_approved=True)
for job in jobs:
    print(job.employer.business_name)  # Extra query for each job!
```

## 📋 Checklist Before Pushing Code

- [ ] Code follows PEP 8 style guide
- [ ] All imports are organized
- [ ] Functions have docstrings
- [ ] Logging is used instead of print()
- [ ] Tests are written and passing
- [ ] No hardcoded secrets or credentials
- [ ] Database queries are efficient
- [ ] Error handling is appropriate
- [ ] Security concerns addressed
- [ ] No debug code left behind

## 🔍 Code Review Checklist

### For Reviewers
- [ ] Does code accomplish its stated goal?
- [ ] Are there any security issues?
- [ ] Are there performance concerns?
- [ ] Is error handling appropriate?
- [ ] Does it follow project conventions?
- [ ] Are tests adequate?
- [ ] Are there any code duplications?

## 📚 Resources

### Django Documentation
- Models: https://docs.djangoproject.com/en/stable/topics/db/models/
- Views: https://docs.djangoproject.com/en/stable/topics/http/views/
- Testing: https://docs.djangoproject.com/en/stable/topics/testing/
- Signals: https://docs.djangoproject.com/en/stable/topics/signals/

### Django REST Framework
- Tutorial: https://www.django-rest-framework.org/tutorial/1-serialization/
- API Guide: https://www.django-rest-framework.org/api-guide/views/

### Best Practices
- Real Python: https://realpython.com/
- Flake8 Style Guide: https://flake8.pycqa.org/
- Django Best Practices: https://docs.djangoproject.com/en/stable/misc/

## 🐛 Debugging Tips

### Django Shell
```bash
python manage.py shell

>>> from jobs.models import Job
>>> jobs = Job.objects.all()
>>> jobs.count()
10
>>> job = jobs.first()
>>> print(job.employer.business_name)
```

### Print Debugging (with Logging)
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Variable value: {variable}")  # Shows in logs
```

### Django Debug Toolbar (for local development)
```bash
pip install django-debug-toolbar

# Add to INSTALLED_APPS and MIDDLEWARE in settings
# Shows queries, performance, etc.
```

### Test-Driven Development
```python
# Write test first
def test_job_application_creates_email():
    # Assertions that email is sent
    pass

# Then implement feature to make test pass
@receiver(post_save, sender=Application)
def send_email_on_application(sender, instance, **kwargs):
    # Send email
    pass
```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] DEBUG = False in settings
- [ ] ALLOWED_HOSTS configured
- [ ] Secret key is strong (50+ chars)
- [ ] Database backed up
- [ ] Static files collected
- [ ] Migrations run
- [ ] Logs directory created
- [ ] Environment variables set
- [ ] SSL certificates valid
- [ ] Tests passing
- [ ] Load testing done
- [ ] Monitoring configured

---

**Last Updated:** April 29, 2026
**Version:** 1.0.0
