from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Settings
    path('settings/', views.admin_settings, name='admin_settings'),
    path('settings/update/', views.admin_settings_update, name='admin_settings_update'),
    path('settings/payment/', views.payment_settings, name='payment_settings'),
    path('settings/shipping/', views.shipping_settings, name='shipping_settings'),
    path('settings/tax/', views.tax_settings, name='tax_settings'),

    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/export/', views.customers_export, name='customers_export'),
    path('customers/send-email/', views.send_customer_email, name='send_customer_email'),

    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:product_id>/images/', views.product_images, name='product_images'),
    path('products/export/', views.products_export, name='products_export'),
    path('products/bulk-update/', views.products_bulk_update, name='products_bulk_update'),

    # Orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
    path('orders/<int:order_id>/send-invoice/', views.send_invoice_email, name='send_invoice_email'),
    path('orders/export/', views.orders_export, name='orders_export'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    path('orders/bulk-action/', views.orders_bulk_action, name='orders_bulk_action'),

    # Testimonials
    path('testimonials/', views.testimonials_list, name='testimonials_list'),
    path('testimonials/<int:testimonial_id>/approve/', views.testimonial_approve, name='testimonial_approve'),
    path('testimonials/<int:testimonial_id>/reject/', views.testimonial_reject, name='testimonial_reject'),
    path('testimonials/<int:testimonial_id>/feature/', views.testimonial_feature, name='testimonial_feature'),
    path('testimonials/<int:testimonial_id>/delete/', views.testimonial_delete, name='testimonial_delete'),

    # Newsletter
    path('newsletter/', views.newsletter_list, name='newsletter_list'),
    path('newsletter/export/', views.newsletter_export, name='newsletter_export'),
    path('newsletter/subscribers/<int:subscriber_id>/activate/', views.newsletter_subscriber_activate, name='newsletter_subscriber_activate'),
    path('newsletter/subscribers/<int:subscriber_id>/deactivate/', views.newsletter_subscriber_deactivate, name='newsletter_subscriber_deactivate'),
    path('newsletter/subscribers/<int:subscriber_id>/delete/', views.newsletter_subscriber_delete, name='newsletter_subscriber_delete'),

    # Newsletter Campaigns
    path('newsletter/campaigns/', views.newsletter_campaigns, name='newsletter_campaigns'),
    path('newsletter/campaigns/create/', views.newsletter_campaign_create, name='newsletter_campaign_create'),
    path('newsletter/campaigns/<int:campaign_id>/edit/', views.newsletter_campaign_edit, name='newsletter_campaign_edit'),
    path('newsletter/campaigns/<int:campaign_id>/delete/', views.newsletter_campaign_delete, name='newsletter_campaign_delete'),
    path('newsletter/campaigns/<int:campaign_id>/send/', views.newsletter_campaign_send, name='newsletter_campaign_send'),

    # Chatbot
    path('chatbot/faqs/', views.chatbot_faqs, name='chatbot_faqs'),
    path('chatbot/quick-responses/', views.chatbot_quick_responses, name='chatbot_quick_responses'),
    path('chatbot/sessions/', views.chatbot_sessions, name='chatbot_sessions'),
    path('chatbot/management/', views.chatbot_management, name='chatbot_management'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),

    # Reports & Analytics
    path('reports/', views.reports, name='reports'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/sales/', views.analytics_sales, name='analytics_sales'),
    path('analytics/customers/', views.analytics_customers, name='analytics_customers'),
    path('analytics/products/', views.analytics_products, name='analytics_products'),
]