import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from cart.models import Order
from cart.utils.pdf import render_to_pdf
from cart.views import download_invoice_pdf, download_pre_payment_invoice

@pytest.mark.django_db
class TestPDFGeneration:
    def setup_method(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(
            user=self.user,
            order_number='TEST123',
            billing_first_name='John',
            billing_last_name='Doe',
            billing_email='john@example.com',
            email='john@example.com',
            billing_phone='1234567890',
        )

    def test_render_to_pdf(self):
        context = {'order': self.order, 'order_items': [], 'request': None}
        response = render_to_pdf('admin_panel/orders/invoice.html', context)
        assert response is not None
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_download_invoice_pdf_view(self):
        request = self.factory.get(reverse('cart:download_invoice_pdf', args=[self.order.id]))
        request.user = self.user
        response = download_invoice_pdf(request, self.order.id)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_download_pre_payment_invoice_view(self):
        request = self.factory.get(reverse('cart:download_pre_payment_invoice', args=[self.order.id]))
        request.user = self.user
        response = download_pre_payment_invoice(request, self.order.id)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

// ... existing code ...
