#!/usr/bin/env python
import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trabaho.settings')
django.setup()

from axes.models import AccessAttempt

logger = logging.getLogger(__name__)

# Clear lockout for localhost
deleted, _ = AccessAttempt.objects.filter(ip_address='127.0.0.1').delete()
logger.info(f"✓ Cleared {deleted} lockout record(s) for 127.0.0.1")
