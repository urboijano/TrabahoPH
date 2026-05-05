# Quick Reference Guide - TrabahoPH

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with required variables
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 2. URLs
- Admin: http://localhost:8000/admin/
- Home: http://localhost:8000/
- Job List: http://localhost:8000/jobs/
- API: http://localhost:8000/api/
- API Docs: http://localhost:8000/api/docs/

## 📱 Common API Calls

### Get Jobs (Paginated)
```bash
curl "http://localhost:8000/api/jobs/?page_size=20"
```

### Filter Jobs by Province
```bash
curl "http://localhost:8000/api/jobs/by_province/?province=Metro%20Manila"
```

### Apply for Job (Requires Auth)
```bash
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1}' \
  -b "sessionid=YOUR_SESSION_ID"
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test jobs.tests

# Run specific test file
python manage.py test jobs.tests.test_models

# Run with coverage
pip install coverage
coverage run --source='jobs' manage.py test jobs.tests
coverage report
```

## 📝 Logging

### View Logs
```bash
# Main log
tail -f logs/django.log

# Security log
tail -f logs/security.log

# Follow new entries
tail -f logs/django.log | grep ERROR
```

### Log Levels
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Development info")      # Level 10
logger.info("General information")    # Level 20
logger.warning("Warning message")     # Level 30
logger.error("Error occurred")        # Level 40
logger.critical("Critical error")     # Level 50
```

## 🔐 Admin Functions

### Approve Jobs (Bulk)
1. Go to http://localhost:8000/admin/jobs/job/
2. Filter by "Pending Review"
3. Select jobs
4. Choose "✓ Approve selected jobs"
5. Click Go

### View Applications for Job
1. Go to http://localhost:8000/admin/jobs/job/
2. Click on a job
3. Scroll to applications section
4. View all applications

### Export Data
```bash
# Dump data
python manage.py dumpdata jobs > backup.json

# Load data
python manage.py loaddata backup.json
```

## 🗄️ Database

### Reset Database (Dev Only!)
```bash
# Delete database
rm db.sqlite3

# Recreate migrations
python manage.py migrate

# Create new admin user
python manage.py createsuperuser
```

### Database Shell
```bash
python manage.py dbshell

# SQLite commands
.tables                    # List tables
.schema jobs_job           # View table structure
SELECT COUNT(*) FROM jobs_job;  # Count records
```

## 📊 Model Queryset Examples

```python
from jobs.models import Job, JobSeeker, Employer, Application

# Jobs
Job.objects.filter(is_active=True, is_approved=True)
Job.objects.filter(province='Metro Manila')
Job.objects.values('category').distinct()

# Job Seekers
JobSeeker.objects.filter(province='Metro Manila')
JobSeeker.objects.exclude(profile_image='')  # Has profile image

# Applications
Application.objects.filter(status='pending')
Application.objects.select_related('job_seeker', 'job')
Application.objects.values('status').annotate(count=Count('id'))

# Employers
Employer.objects.filter(dti_permit__isnull=False)  # Has DTI permit
```

## 🔧 Common Commands

```bash
# Create migration
python manage.py makemigrations apps

# Apply migration
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Collect static files
python manage.py collectstatic --noinput

# Clear cache
python manage.py clear_cache

# Check for issues
python manage.py check

# Get Django shell
python manage.py shell

# Run custom command
python manage.py runserver_plus

# Format code (install black: pip install black)
black jobs/

# Check code style (install flake8: pip install flake8)
flake8 jobs/
```

## 🐛 Debugging

### Django Debug Toolbar
```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Print to Console (with logging)
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Current value: {variable}")
logger.info(f"User: {user.username}")

# Check logs/django.log
```

### Interactive Debugging
```python
import pdb
pdb.set_trace()  # Execution stops here
```

## 📋 File Locations

```
Project Root:
├── jobs/                      # Main app
│   ├── models.py             # Models definition
│   ├── views.py              # View logic
│   ├── admin.py              # Admin interface
│   ├── urls.py               # URL routing
│   ├── serializers.py        # API serializers
│   ├── validators.py         # File validators
│   ├── signals.py            # Event handlers
│   └── tests/                # Test suite
│
├── logs/                      # Application logs
│   ├── django.log            # Main log
│   └── security.log          # Security log
│
├── media/                     # User uploads
│   ├── dti_permits/          # DTI permit files
│   └── profile_images/       # Profile pictures
│
├── trabaho/
│   ├── settings.py           # Django config
│   ├── urls.py              # Project URLs
│   └── wsgi.py              # WSGI config
│
├── requirements.txt          # Dependencies
└── manage.py                 # Django CLI
```

## 🔑 Environment Variables

Required in `.env`:
```
SECRET_KEY                    # Django secret key (50+ chars)
DEBUG                         # True/False
ALLOWED_HOSTS                 # Comma-separated hosts
EMAIL_HOST_USER              # Gmail address
EMAIL_HOST_PASSWORD          # Gmail app password
RECAPTCHA_SITE_KEY           # (optional)
RECAPTCHA_SECRET_KEY         # (optional)
GEMINI_API_KEY               # (optional)
```

## 🚨 Common Issues & Solutions

### Issue: "No such table: jobs_job"
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: "Static files not loading in production"
**Solution:** Collect static files
```bash
python manage.py collectstatic
```

### Issue: "Email not sending"
**Solution:** Check email configuration
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- Check logs/django.log for errors
- Ensure Gmail app password (not account password)

### Issue: "Permission denied on logs"
**Solution:** Create logs directory
```bash
mkdir -p logs
chmod 755 logs
```

### Issue: "Database locked"
**Solution:** Stop other processes, delete db.sqlite3 if safe
```bash
pkill -f runserver
rm db.sqlite3
python manage.py migrate
```

## 📚 Documentation Files

- `API_DOCUMENTATION.md` - Complete API reference
- `IMPLEMENTATION_SUMMARY.md` - What was implemented
- `DEVELOPMENT_GUIDELINES.md` - Coding standards
- `README.md` - Project overview
- `SECURITY.md` - Security best practices

## 🎯 Key Features

| Feature | Endpoint | Status |
|---------|----------|--------|
| Job Listing | `/api/jobs/` | ✓ |
| Job Details | `/api/jobs/{id}/` | ✓ |
| Applications | `/api/applications/` | ✓ |
| Admin Approval | Admin Panel | ✓ |
| Email Notifications | Auto-triggered | ✓ |
| File Upload Validation | On upload | ✓ |
| Error Logging | Automatic | ✓ |
| Profile Images | User Profile | ✓ |

## 💡 Tips & Tricks

1. **Use `select_related()` for ForeignKey queries**
   ```python
   apps = Application.objects.select_related('job_seeker', 'job')
   ```

2. **Use `prefetch_related()` for reverse FK queries**
   ```python
   jobs = Job.objects.prefetch_related('applications')
   ```

3. **Use `values()` to get only specific fields**
   ```python
   titles = Job.objects.values_list('title', flat=True)
   ```

4. **Always validate user input**
   ```python
   from .validators import DTIPermitValidator
   DTIPermitValidator.validate(file)
   ```

5. **Log important actions**
   ```python
   logger.info(f"Admin {user} approved job {job_id}")
   ```

---

## 🆘 Quick Help

**Need more info?**
- API Documentation: See `API_DOCUMENTATION.md`
- Implementation Details: See `IMPLEMENTATION_SUMMARY.md`
- Development Standards: See `DEVELOPMENT_GUIDELINES.md`

**Let's Code! 🚀**
