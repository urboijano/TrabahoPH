from django.core.management.base import BaseCommand
from axes.models import AccessAttempt


class Command(BaseCommand):
    help = 'Clear IP-based account lockouts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ip',
            type=str,
            help='Clear lockout for specific IP address',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all lockouts',
        )

    def handle(self, *args, **options):
        if options['all']:
            deleted, _ = AccessAttempt.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleared {deleted} lockout record(s)')
            )
        elif options['ip']:
            ip = options['ip']
            deleted, _ = AccessAttempt.objects.filter(ip_address=ip).delete()
            if deleted:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared lockout for {ip}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'No lockout found for {ip}')
                )
        else:
            # Default: clear localhost
            deleted, _ = AccessAttempt.objects.filter(ip_address='127.0.0.1').delete()
            if deleted:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared lockout for 127.0.0.1 (localhost)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No lockout found for 127.0.0.1')
                )
