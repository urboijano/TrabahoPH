"""
Custom runserver command that automatically enables HTTPS if certificates exist.
Run with: python manage.py runserver
"""

import os
import sys
from pathlib import Path
from django.core.management.commands.runserver import Command as BaseRunserverCommand


class Command(BaseRunserverCommand):
    help = "Starts a development server with automatic HTTPS if certificates exist"

    def handle(self, *args, **options):
        """Override handle to check for HTTPS certificates"""
        
        # Get the project base directory
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        cert_file = base_dir / 'localhost.crt'
        key_file = base_dir / 'localhost.key'
        
        # Check if SSL certificates exist
        if cert_file.exists() and key_file.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ HTTPS certificates detected!\n"
                    f"  Certificate: {cert_file}\n"
                    f"  Private Key: {key_file}\n"
                )
            )
            
            try:
                # Try to import and use django_extensions runserver_plus
                from django_extensions.management.commands.runserver_plus import Command as PlusRunserverCommand
                
                self.stdout.write(
                    self.style.SUCCESS(
                        "Starting development server with HTTPS enabled...\n"
                        "⚠️  Browser may show a security warning (normal for self-signed certificates)\n"
                    )
                )
                
                # Create a new instance of runserver_plus
                plus_command = PlusRunserverCommand()
                
                # Prepare options for runserver_plus
                plus_options = options.copy()
                plus_options['cert_file'] = str(cert_file)
                plus_options['key_file'] = str(key_file)
                
                return plus_command.handle(*args, **plus_options)
                
            except ImportError:
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠️  django-extensions not installed. Running with regular HTTP.\n"
                        "   Install with: pip install django-extensions\n"
                        "   Then certificates will be automatically used.\n"
                    )
                )
        else:
            if not cert_file.exists() or not key_file.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠️  SSL certificates not found. Running with HTTP.\n"
                        "   Generate certificates with: python generate_certificate.py\n"
                        "   Then automatic HTTPS will be enabled.\n"
                    )
                )
        
        # Fall back to regular runserver
        return super().handle(*args, **options)
