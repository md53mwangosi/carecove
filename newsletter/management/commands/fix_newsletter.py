from django.core.management.base import BaseCommand
from newsletter.models import Newsletter


class Command(BaseCommand):
    help = 'Fix newsletter schema issues'

    def handle(self, *args, **options):
        # Fix any newsletter issues
        count = Newsletter.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'Found {count} active newsletter subscriptions')
        )