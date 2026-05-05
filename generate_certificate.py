#!/usr/bin/env python
"""
Generate a self-signed SSL certificate for local HTTPS development.
Run this script before running the development server with HTTPS.

Usage:
    python generate_certificate.py
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from OpenSSL import crypto

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Certificate file paths
CERT_FILE = PROJECT_ROOT / 'localhost.crt'
KEY_FILE = PROJECT_ROOT / 'localhost.key'

def generate_certificate():
    """Generate a self-signed certificate for localhost using pyOpenSSL"""
    
    if CERT_FILE.exists() and KEY_FILE.exists():
        logger.info("✓ Certificate files already exist:")
        logger.info(f"  - {CERT_FILE}")
        logger.info(f"  - {KEY_FILE}")
        return True
    
    logger.info("Generating self-signed SSL certificate for localhost...")
    
    try:
        # Create a key pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        
        # Create a self-signed certificate
        cert = crypto.X509()
        cert.get_subject().C = "PH"
        cert.get_subject().ST = "State"
        cert.get_subject().L = "City"
        cert.get_subject().O = "TrabahoPH"
        cert.get_subject().CN = "localhost"
        
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 365 days
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Write the certificate to file
        with open(CERT_FILE, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        
        # Write the key to file
        with open(KEY_FILE, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        
        logger.info("\n✓ Certificate generated successfully!")
        logger.info(f"  Certificate: {CERT_FILE}")
        logger.info(f"  Private Key: {KEY_FILE}")
        logger.info("\nTo run the development server with HTTPS, use:")
        logger.info("  python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key")
        logger.info("\nNote: Your browser may show a security warning about the self-signed certificate.")
        logger.info("This is normal for local development. Click 'Proceed' or 'Advanced' and continue.")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Error generating certificate: {e}")
        return False

if __name__ == '__main__':
    success = generate_certificate()
    exit(0 if success else 1)

