from django.core.management.base import BaseCommand
from django.conf import settings
from cart.pesapal import PesapalService

class Command(BaseCommand):
    help = 'Register Pesapal IPN URL and get IPN ID'

    def handle(self, *args, **options):
        pesapal = PesapalService()
        ipn_url = getattr(settings, 'PESAPAL_IPN_URL', None)
        if not ipn_url:
            self.stdout.write(self.style.ERROR('PESAPAL_IPN_URL setting is not configured.'))
            return

        self.stdout.write(f'Registering IPN URL: {ipn_url}')
        ipn_id = pesapal.register_ipn_url(ipn_url)
        if ipn_id:
            self.stdout.write(self.style.SUCCESS(f'Successfully registered IPN URL. IPN ID: {ipn_id}'))
            self.stdout.write('Please add this IPN ID to your environment variables as PESAPAL_IPN_ID.')
        else:
            self.stdout.write(self.style.ERROR('Failed to register IPN URL.'))
