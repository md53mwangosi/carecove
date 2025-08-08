from django.core.management.base import BaseCommand
from newsletter.models import Newsletter, EmailCampaign


class Command(BaseCommand):
    help = 'Test newsletter functionality'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Test email address')

    def handle(self, *args, **options):
        email = options.get('email', 'test@example.com')

        # Create test campaign
        campaign = EmailCampaign.objects.create(
            subject='Test Campaign',
            content='This is a test campaign',
            subject_sw='Kampeni ya Majaribio',
            content_sw='Hii ni kampeni ya majaribio'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Created test campaign: {campaign.subject}')
        )