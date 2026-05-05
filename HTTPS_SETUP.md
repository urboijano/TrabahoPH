# HTTPS Setup for Local Development

## Overview
This guide explains how to enable HTTPS for local development in TrabahoPH, even though you're using localhost.

## Prerequisites
- OpenSSL installed on your system
- All packages from `requirements.txt` installed

## Installation Steps

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

This includes:
- `django-extensions` - Enables `runserver_plus` with HTTPS support
- `pyOpenSSL` - SSL certificate handling
- `Werkzeug` - WSGI utilities

### 2. Generate Self-Signed Certificate
Run the certificate generation script:

```bash
python generate_certificate.py
```

This will create two files in your project root:
- `localhost.crt` - SSL Certificate
- `localhost.key` - Private key

### 3. Run Development Server with HTTPS

```bash
python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key
```

Or if you prefer HTTP for testing:
```bash
python manage.py runserver
```

## Accessing the Application

### With HTTPS (Secure)
- URL: `https://127.0.0.1:8000`
- Browser may show security warning (normal for self-signed certificates)
- Click "Advanced" and proceed to continue

### With HTTP (Unrestricted)
- URL: `http://127.0.0.1:8000`

## Browser Security Warnings

When using self-signed certificates, your browser will display a security warning. This is **normal and expected** for local development. The warning appears because:

1. The certificate is not signed by a trusted Certificate Authority (CA)
2. The certificate is self-signed for testing only

### Chrome/Edge:
1. Click "Advanced"
2. Click "Proceed to 127.0.0.1 (unsafe)"

### Firefox:
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

### Safari:
1. The page will not load initially
2. Go to keychain and trust the certificate, or use Chrome/Firefox

## Security Settings

The following security headers are enabled:
- **SESSION_COOKIE_SECURE**: Cookies only sent over HTTPS
- **CSRF_COOKIE_SECURE**: CSRF tokens only sent over HTTPS
- **SECURE_HSTS_SECONDS**: HTTP Strict Transport Security (1 year)
- **SECURE_BROWSER_XSS_FILTER**: XSS protection enabled
- **SECURE_CONTENT_SECURITY_POLICY**: CSP headers

For local development (DEBUG=True), these settings are relaxed to allow HTTP access.

## Troubleshooting

### OpenSSL not found
If you see "openssl is not installed or not in PATH":

**Windows:**
- Download and install from: https://slproweb.com/products/Win32OpenSSL.html
- Add OpenSSL to your system PATH

**macOS:**
```bash
brew install openssl
```

**Linux:**
```bash
sudo apt-get install openssl
```

### Certificate already exists
If you want to regenerate the certificate, delete the existing files first:
```bash
rm localhost.crt localhost.key
python generate_certificate.py
```

### Port already in use
If port 8000 is already in use:
```bash
python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key 8001
```

## For Production

When deploying to production:
1. Set `DEBUG = False` in settings.py
2. Obtain a proper SSL certificate from a Certificate Authority (Let's Encrypt, etc.)
3. Set `SECURE_SSL_REDIRECT = True`
4. Use a production WSGI server (Gunicorn, uWSGI, etc.)
5. Configure your web server (Nginx, Apache) for SSL termination
