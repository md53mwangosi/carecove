
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from admin_panel.models import Order

class AdminPanelViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.order = Order.objects.create(
            user=self.user,
            order_number='TEST123',
            billing_first_name='John',
            billing_last_name='Doe',
            billing_email='john@example.com',
            email='john@example.com',
            billing_phone='1234567890',
        )

    def test_send_invoice_email(self):
        self.client.login(username='admin', password='adminpass')
        url = reverse('admin_panel:send_invoice_email', args=[self.order.id])

        with patch('admin_panel.views.render_to_pdf') as mock_render_to_pdf:
            mock_render_to_pdf.return_value = type('obj', (object,), {'content': b'%PDF-1.4'})()
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

# Additional test methods can be added here
