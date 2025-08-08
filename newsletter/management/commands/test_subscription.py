from django.core.management.base import BaseCommand
from newsletter.models import Newsletter
# Removed import of NewsletterForm as it is unused

class Command(BaseCommand):
    help = 'Test newsletter subscription functionality'

    def handle(self, *args, **options):
        # Test subscription
        test_email = 'test@example.com'

        # Create test subscription
        Newsletter.objects.create(
            email=test_email,
            name='Test User',
            language_preference='en',
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created test subscription')
        )