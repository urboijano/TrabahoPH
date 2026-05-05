"""
Django settings for trabaho project.
"""

from pathlib import Path
import os
import sys
import warnings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file - explicitly tell python-decouple where to find it
from dotenv import load_dotenv
load_dotenv(str(BASE_DIR / '.env'))

# Helper function to load config from environment
def get_config(key, default=None, cast=None):
    """Load configuration from environment or .env file"""
    value = None
    
    try:
        from decouple import config as decouple_config
        # Try to get from environment/decouple
        if cast == bool:
            value = decouple_config(key, default=str(default).lower() if default is not None else 'false', cast=bool)
        elif cast == int:
            value = decouple_config(key, default=str(default) if default is not None else '0', cast=int)
        else:
            # For list or string types, just get the raw value
            raw = decouple_config(key, default=None) 
            value = raw if raw is not None else default
    except (ImportError, Exception):
        pass
    
    # If decouple didn't work or we need fallback, use os.getenv
    if value is None:
        value = os.getenv(key, default)
    
    # Apply casting if needed
    if cast == list and isinstance(value, str):
        value = [v.strip() for v in value.split(',')]
    elif cast == bool and isinstance(value, str):
        value = value.lower() in ('true', '1', 'yes')
    elif cast == int and isinstance(value, str):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = default
    
    return value

# Load environment variables from .env file
SECRET_KEY = get_config('SECRET_KEY', default='django-insecure-CHANGE-IN-PRODUCTION-MIN-50-CHARS')
DEBUG = get_config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = get_config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=list)

# Error logging - capture errors even in production
LOGGING_FOR_ERRORS = get_config('LOGGING_FOR_ERRORS', default=not DEBUG, cast=bool)

# ===== PRODUCTION SECURITY CHECKS =====
# Warn or block if running in production with insecure settings
if not DEBUG:
    # Check SECRET_KEY length (minimum 50 characters for security)
    if len(SECRET_KEY) < 50:
        warnings.warn(
            'SECRET_KEY is too short! Use a key with at least 50 characters.',
            RuntimeWarning
        )
    
    # Check if running with DEBUG=True in production
    if DEBUG:
        raise RuntimeError(
            'SECURITY ERROR: DEBUG must be False in production! '
            'Set DEBUG=False in your environment variables.'
        )
    
    # Check if ALLOWED_HOSTS contains wildcard
    if '*' in ALLOWED_HOSTS:
        raise RuntimeError(
            'SECURITY ERROR: ALLOWED_HOSTS contains wildcard "*"! '
            'This is insecure in production. Specify explicit hosts.'
        )
    
    # Check if ALLOWED_HOSTS is not empty
    if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
        raise RuntimeError(
            'SECURITY ERROR: ALLOWED_HOSTS is empty! '
            'You must specify at least one valid hostname.'
        )

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# HTTPS/SSL Settings - environment-aware
SECURE_SSL_REDIRECT = get_config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = get_config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = get_config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = get_config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)
SECURE_HSTS_SECONDS = get_config('SECURE_HSTS_SECONDS', default=31536000 if not DEBUG else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG, cast=bool)
SECURE_HSTS_PRELOAD = get_config('SECURE_HSTS_PRELOAD', default=not DEBUG, cast=bool)
SECURE_BROWSER_XSS_FILTER = True

# Content Security Policy - updated to support dynamic content needs
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "www.google.com", "www.gstatic.com"),
    "style-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'", "cdn.jsdelivr.net", "fonts.googleapis.com"),
    "frame-src": ("'self'", "www.google.com"),
    "connect-src": ("'self'", "https://www.google.com", "https://generativelanguage.googleapis.com"),
}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',  # Django REST Framework
    'django_filters',  # For filtering API results
    'axes',  # For rate limiting and account lockout
    'jobs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # For rate limiting - must be after AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trabaho.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'jobs', 'templates')],  # Include templates directory for error pages
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trabaho.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Increased from default 8 chars
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom password complexity validator
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = True


# ===== LOGGING CONFIGURATION =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'timestamp': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'jobs': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Ensure logs directory exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'jobs', 'static'),
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = 'auth'
LOGIN_REDIRECT_URL = 'index'

# Google reCAPTCHA Settings - use environment variables
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')

# Warn if reCAPTCHA not configured in production
if not DEBUG and (not RECAPTCHA_SITE_KEY or not RECAPTCHA_SECRET_KEY):
    warnings.warn(
        'reCAPTCHA keys not configured! Set RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY.',
        RuntimeWarning
    )


# Email Configuration - use environment variables
# For production with Gmail SMTP:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')  # Your Gmail address
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # App password (spaces removed)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'noreply@trabahoph.com')

# Warn if email not configured in production
if not DEBUG and not EMAIL_HOST_USER:
    warnings.warn(
        'Email not configured! Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD for password reset functionality.',
        RuntimeWarning
    )

# For testing/development, uncomment the line below to see emails in console:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===== DJANGO-AXES RATE LIMITING CONFIGURATION =====
# Rate limiting for all authentication attempts (login, register, etc.)
AXES_FAILURE_LIMIT = 5  # Lock account after 5 failed attempts
AXES_COOLOFF_DURATION = 600  # 10 minutes cooloff period
AXES_LOCKOUT_TEMPLATE = 'axes/lockout.html'
AXES_RESET_ON_SUCCESS = True
AXES_VERBOSE = True  # Log attempts

# Authentication backends for rate limiting
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # django-axes rate limiting backend
    'django.contrib.auth.backends.ModelBackend',  # Django's default authentication
]

# Django Messages Configuration
from django.contrib.messages import constants as messages_constants
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'info',
    messages_constants.INFO: 'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR: 'error',
}

# ===== DJANGO REST FRAMEWORK CONFIGURATION =====
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
}