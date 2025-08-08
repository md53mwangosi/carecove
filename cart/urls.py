
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart, name='update_cart'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/invoice/<int:order_id>/', views.pre_payment_invoice, name='pre_payment_invoice'),
    path('checkout/invoice/<int:order_id>/download/', views.download_pre_payment_invoice, name='download_pre_payment_invoice'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/invoice/', views.customer_invoice, name='customer_invoice'),
    path('pesapal-callback/<str:order_number>/', views.pesapal_callback, name='pesapal_callback'),
    path('pesapal-ipn/', views.pesapal_ipn, name='pesapal_ipn'),
    path('orders/<int:order_id>/download-invoice/', views.download_invoice_pdf, name='download_invoice_pdf'),
]
