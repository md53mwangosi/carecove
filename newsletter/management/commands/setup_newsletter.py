from django.core.management.base import BaseCommand
from newsletter.models import Newsletter, EmailCampaign


class Command(BaseCommand):
    help = 'Setup initial newsletter data'

    def handle(self, *args, **options):
        # Create sample newsletter subscriptions
        sample_emails = [
            'customer1@example.com',
            'customer2@example.com',
            'customer3@example.com'
        ]

        for email in sample_emails:
            Newsletter.objects.get_or_create(
                email=email,
                defaults={
                    'name': f'Customer {email.split("@")[0]}',
                    'language_preference': 'en',
                    'is_active': True
                }
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully setup newsletter data')
        )