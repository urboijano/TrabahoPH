"""
Management command to check security configurations on startup.
Run this before deploying to production to verify all security settings.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import warnings


class Command(BaseCommand):
    help = 'Verify security configurations for production deployment'

    def handle(self, *args, **options):
        security_issues = []
        security_warnings = []
        
        self.stdout.write(self.style.HTTP_INFO('Checking Django Security Configuration...'))
        self.stdout.write('')
        
        # ===== CRITICAL CHECKS =====
        self.stdout.write(self.style.HTTP_SERVER_ERROR('CRITICAL CHECKS:'))
        
        # Check DEBUG setting
        if settings.DEBUG:
            security_issues.append(
                'DEBUG is set to True in production! Set DEBUG=False in environment variables.'
            )
            self.stdout.write(self.style.ERROR('  ✗ DEBUG=True (CRITICAL ISSUE)'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ DEBUG=False'))
        
        # Check ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS:
            security_issues.append(
                'ALLOWED_HOSTS contains wildcard "*"! Specify explicit hostnames.'
            )
            self.stdout.write(self.style.ERROR('  ✗ ALLOWED_HOSTS=[\'*\'] (CRITICAL ISSUE)'))
        elif not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['']:
            security_issues.append(
                'ALLOWED_HOSTS is empty! Specify at least one valid hostname.'
            )
            self.stdout.write(self.style.ERROR('  ✗ ALLOWED_HOSTS is empty (CRITICAL ISSUE)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}'))
        
        # Check SECRET_KEY length
        if len(settings.SECRET_KEY) < 50 or 'CHANGE' in settings.SECRET_KEY.upper():
            security_issues.append(
                'SECRET_KEY is not strong enough! Use a key with at least 50 characters.'
            )
            self.stdout.write(self.style.ERROR('  ✗ SECRET_KEY is too short or default'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ SECRET_KEY is strong'))
        
        self.stdout.write('')
        
        # ===== HIGH PRIORITY CHECKS =====
        self.stdout.write(self.style.WARNING('HIGH PRIORITY CHECKS:'))
        
        # Check HTTPS/SSL settings
        if not settings.DEBUG:
            if not settings.SECURE_SSL_REDIRECT:
                security_warnings.append('SECURE_SSL_REDIRECT should be True in production')
                self.stdout.write(self.style.WARNING('  ⚠ SECURE_SSL_REDIRECT=False'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ SECURE_SSL_REDIRECT=True'))
            
            if not settings.SESSION_COOKIE_SECURE:
                security_warnings.append('SESSION_COOKIE_SECURE should be True in production')
                self.stdout.write(self.style.WARNING('  ⚠ SESSION_COOKIE_SECURE=False'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ SESSION_COOKIE_SECURE=True'))
            
            if not settings.SESSION_COOKIE_HTTPONLY:
                security_warnings.append('SESSION_COOKIE_HTTPONLY should be True')
                self.stdout.write(self.style.WARNING('  ⚠ SESSION_COOKIE_HTTPONLY=False'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ SESSION_COOKIE_HTTPONLY=True'))
            
            if not settings.CSRF_COOKIE_SECURE:
                security_warnings.append('CSRF_COOKIE_SECURE should be True in production')
                self.stdout.write(self.style.WARNING('  ⚠ CSRF_COOKIE_SECURE=False'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ CSRF_COOKIE_SECURE=True'))
        
        self.stdout.write('')
        
        # ===== MEDIUM PRIORITY CHECKS =====
        self.stdout.write(self.style.HTTP_NOT_FOUND('MEDIUM PRIORITY CHECKS:'))
        
        # Check reCAPTCHA configuration
        if not settings.RECAPTCHA_SITE_KEY or not settings.RECAPTCHA_SECRET_KEY:
            security_warnings.append('reCAPTCHA keys not configured')
            self.stdout.write(self.style.WARNING('  ⚠ reCAPTCHA not configured'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ reCAPTCHA configured'))
        
        # Check email configuration
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            security_warnings.append('Email not configured (needed for password reset)')
            self.stdout.write(self.style.WARNING('  ⚠ Email not configured'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Email configured'))
        
        # Check axes (rate limiting) is installed
        if 'axes' not in settings.INSTALLED_APPS:
            security_warnings.append('django-axes not installed (rate limiting disabled)')
            self.stdout.write(self.style.WARNING('  ⚠ django-axes not installed'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ django-axes installed (rate limiting enabled)'))
        
        self.stdout.write('')
        
        # ===== DISPLAY SUMMARY =====
        self.stdout.write(self.style.HTTP_INFO('SUMMARY:'))
        self.stdout.write('')
        
        if security_issues:
            self.stdout.write(self.style.ERROR(f'CRITICAL ISSUES FOUND: {len(security_issues)}'))
            for i, issue in enumerate(security_issues, 1):
                self.stdout.write(self.style.ERROR(f'  {i}. {issue}'))
            self.stdout.write('')
            return  # Exit with failure
        
        if security_warnings:
            self.stdout.write(self.style.WARNING(f'Warnings: {len(security_warnings)}'))
            for i, warning in enumerate(security_warnings, 1):
                self.stdout.write(self.style.WARNING(f'  {i}. {warning}'))
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('✓ All critical security checks passed!'))
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Deployment Checklist:'))
        self.stdout.write('  [ ] Configure all environment variables from .env.example')
        self.stdout.write('  [ ] Run: python manage.py migrate')
        self.stdout.write('  [ ] Set DEBUG=False')
        self.stdout.write('  [ ] Set ALLOWED_HOSTS to your production domain')
        self.stdout.write('  [ ] Use a strong SECRET_KEY (50+ characters)')
        self.stdout.write('  [ ] Enable HTTPS (SECURE_SSL_REDIRECT=True)')
        self.stdout.write('  [ ] Configure email for password reset functionality')
        self.stdout.write('  [ ] Configure reCAPTCHA keys')
        self.stdout.write('  [ ] Run: python manage.py check_security')
