from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
import csv
import io
import logging
from decimal import Decimal
from datetime import datetime, timedelta

# Import models
from shop.models import Product, Category, ProductReview
from cart.models import Order, OrderItem
from accounts.models import UserProfile
from testimonials.models import Testimonial
from newsletter.models import Newsletter, EmailCampaign
from chatbot.models import ChatbotFAQ, QuickResponse, ChatSession

# Import decorators
from .decorators import admin_required

logger = logging.getLogger(__name__)


@admin_required
def dashboard(request):
    """Admin dashboard with overview statistics."""

    # Get basic statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_customers = UserProfile.objects.count()
    total_revenue = Order.objects.filter(
        payment_status='completed'
    ).aggregate(total=Sum('total'))['total'] or 0

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Low stock products
    low_stock_products = Product.objects.filter(
        track_inventory=True,
        stock_quantity__lte=10
    ).order_by('stock_quantity')[:10]

    # Pending orders
    pending_orders = Order.objects.filter(
        payment_status='pending'
    ).count()

    # Pending testimonials
    pending_testimonials = Testimonial.objects.filter(
        status='pending'
    ).count()

    # Newsletter subscribers
    newsletter_subscribers = Newsletter.objects.filter(
        is_active=True
    ).count()

    # Monthly sales data for chart
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    daily_sales = Order.objects.filter(
        payment_status='completed',
        created_at__range=[start_date, end_date]
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        total=Sum('total')
    ).order_by('day')

    # Prepare chart data
    sales_data = []
    labels = []
    for sale in daily_sales:
        labels.append(sale['day'].strftime('%b %d'))
        sales_data.append(float(sale['total']))

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'pending_orders': pending_orders,
        'pending_testimonials': pending_testimonials,
        'newsletter_subscribers': newsletter_subscribers,
        'sales_labels': json.dumps(labels),
        'sales_data': json.dumps(sales_data),
    }

    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def products_list(request):
    """Display list of products in admin panel."""

    # Get all products
    products = Product.objects.all()

    # Apply filters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if status_filter:
        if status_filter == 'active':
            products = products.filter(is_active=True)
        elif status_filter == 'inactive':
            products = products.filter(is_active=False)
        elif status_filter == 'featured':
            products = products.filter(is_featured=True)
        elif status_filter == 'low_stock':
            products = products.filter(stock_quantity__lte=10)

    # Apply sorting
    valid_sort_fields = [
        'name', '-name', 'price', '-price', 'stock_quantity', '-stock_quantity',
        'created_at', '-created_at'
    ]
    if sort_by in valid_sort_fields:
        products = products.order_by(sort_by)

    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # Get categories for filter
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }

    return render(request, 'admin_panel/products/list.html', context)



@admin_required
def admin_settings(request):
    """Display admin settings page."""
    return render(request, 'admin_panel/settings.html')


@admin_required
def admin_settings_update(request):
    """Update admin settings."""
    if request.method == 'POST':
        # Handle settings update logic here
        messages.success(request, 'Settings updated successfully!')
    return redirect('admin_panel:admin_settings')



@admin_required
def product_add(request):
    """Add a new product."""
    from shop.forms import ProductForm

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('admin_panel:products_list')
    else:
        form = ProductForm()

    categories = Category.objects.all()

    context = {
        'form': form,
        'categories': categories,
    }

    return render(request, 'admin_panel/products/add.html', context)


@admin_required
def product_edit(request, product_id):
    """Edit an existing product."""
    from shop.forms import ProductForm

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('admin_panel:products_list')
    else:
        form = ProductForm(instance=product)

    categories = Category.objects.all()

    context = {
        'form': form,
        'product': product,
        'categories': categories,
    }

    return render(request, 'admin_panel/products/edit.html', context)


@admin_required
def product_delete(request, product_id):
    """Delete a product."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
        return redirect('admin_panel:products_list')

    context = {
        'product': product,
    }

    return render(request, 'admin_panel/products/delete.html', context)


@admin_required
def product_images(request, product_id):
    """Manage product images."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle image upload
        images = request.FILES.getlist('images')
        for image in images:
            product.images.create(image=image)
        messages.success(request, 'Images uploaded successfully.')
        return redirect('admin_panel:product_images', product_id=product_id)

    context = {
        'product': product,
    }

    return render(request, 'admin_panel/products/images.html', context)


@admin_required
def payment_settings(request):
    """Display payment settings page."""
    return render(request, 'admin_panel/payment_settings.html')


@admin_required
def shipping_settings(request):
    """Display shipping settings page."""
    return render(request, 'admin_panel/shipping_settings.html')


@admin_required
def tax_settings(request):
    """Display tax settings page."""
    return render(request, 'admin_panel/tax_settings.html')


@admin_required
def customers_list(request):
    """Display list of customers."""
    customers = UserProfile.objects.select_related('user').order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/customers/list.html', context)


@admin_required
def customer_detail(request, customer_id):
    """Display customer details."""
    customer = get_object_or_404(UserProfile, id=customer_id)

    # Get customer orders
    orders = Order.objects.filter(user=customer.user).order_by('-created_at')
    orders_count = orders.count()
    total_spent = orders.filter(payment_status='completed').aggregate(
        total=Sum('total')
    )['total'] or 0

    context = {
        'customer': customer,
        'orders': orders[:10],  # Recent 10 orders
        'orders_count': orders_count,
        'total_spent': total_spent,
    }
    return render(request, 'admin_panel/customers/detail.html', context)


@admin_required
def customers_export(request):
    """Export customers to CSV."""
    customers = UserProfile.objects.select_related('user').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Date Joined', 'Orders Count'])

    for customer in customers:
        orders_count = Order.objects.filter(user=customer.user).count()
        writer.writerow([
            f"{customer.user.first_name} {customer.user.last_name}",
            customer.user.email,
            customer.phone,
            customer.created_at.strftime('%Y-%m-%d'),
            orders_count
        ])

    return response


@admin_required
def products_export(request):
    """Export products to CSV or PDF."""
    format_type = request.GET.get('format', 'csv')

    # Get filtered products
    products = Product.objects.all()

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if status_filter:
        if status_filter == 'active':
            products = products.filter(is_active=True)
        elif status_filter == 'inactive':
            products = products.filter(is_active=False)

    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'SKU', 'Category', 'Price', 'Stock', 'Status', 'Created At'
        ])

        for product in products:
            writer.writerow([
                product.name,
                product.sku,
                product.category.name if product.category else '',
                product.price,
                product.stock_quantity,
                'Active' if product.is_active else 'Inactive',
                product.created_at.strftime('%Y-%m-%d')
            ])

        return response

    elif format_type == 'pdf':
        # For PDF export, we'll use a simple HTML response
        html = f"""
        <html>
        <head><title>Products Report</title></head>
        <body>
            <h1>Products Report</h1>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>SKU</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
        """

        for product in products:
            html += f"""
                    <tr>
                        <td>{product.name}</td>
                        <td>{product.sku}</td>
                        <td>{product.category.name if product.category else ''}</td>
                        <td>{product.price}</td>
                        <td>{product.stock_quantity}</td>
                        <td>{'Active' if product.is_active else 'Inactive'}</td>
                        <td>{product.created_at.strftime('%Y-%m-%d')}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="products.html"'
        return response

    return redirect('admin_panel:products_list')


@admin_required
@require_POST
def products_bulk_update(request):
    """Bulk update products."""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return JsonResponse({'error': 'No products selected'}, status=400)

        products = Product.objects.filter(id__in=product_ids)

        if action == 'activate':
            products.update(is_active=True)
            message = f'{products.count()} products activated successfully'
        elif action == 'deactivate':
            products.update(is_active=False)
            message = f'{products.count()} products deactivated successfully'
        elif action == 'delete':
            count = products.count()
            products.delete()
            message = f'{count} products deleted successfully'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error in products bulk update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@require_POST
def send_customer_email(request):
    """Send email to customer."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([email, subject, message]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@admin_required
def testimonials_list(request):
    """Display list of testimonials."""
    testimonials = Testimonial.objects.all().order_by('-created_at')

    # Apply filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        testimonials = testimonials.filter(status=status_filter)

    paginator = Paginator(testimonials, 20)
    page = request.GET.get('page')
    testimonials = paginator.get_page(page)

    context = {
        'testimonials': testimonials,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/testimonials/list.html', context)


@admin_required
@require_POST
def testimonial_approve(request, testimonial_id):
    """Approve a testimonial."""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.status = 'approved'
    testimonial.save()
    messages.success(request, 'Testimonial approved successfully.')
    return redirect('admin_panel:testimonials_list')


@admin_required
@require_POST
def testimonial_reject(request, testimonial_id):
    """Reject a testimonial."""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.status = 'rejected'
    testimonial.save()
    messages.success(request, 'Testimonial rejected successfully.')
    return redirect('admin_panel:testimonials_list')


@admin_required
@require_POST
def testimonial_feature(request, testimonial_id):
    """Feature/unfeature a testimonial."""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.is_featured = not testimonial.is_featured
    testimonial.save()
    messages.success(request, 'Testimonial featured status updated.')
    return redirect('admin_panel:testimonials_list')


@admin_required
@require_POST
def testimonial_delete(request, testimonial_id):
    """Delete a testimonial."""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.delete()
    messages.success(request, 'Testimonial deleted successfully.')
    return redirect('admin_panel:testimonials_list')


@admin_required
def newsletter_list(request):
    """Display newsletter subscribers."""
    subscribers = Newsletter.objects.all().order_by('-subscribed_at')

    # Apply filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        subscribers = subscribers.filter(is_active=(status_filter == 'active'))

    search_query = request.GET.get('search', '')
    if search_query:
        subscribers = subscribers.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    paginator = Paginator(subscribers, 20)
    page = request.GET.get('page')
    subscribers = paginator.get_page(page)

    context = {
        'subscribers': subscribers,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/newsletter/list.html', context)


@admin_required
def newsletter_export(request):
    """Export newsletter subscribers."""
    subscribers = Newsletter.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email', 'Name', 'Language', 'Status', 'Subscribed At'])

    for subscriber in subscribers:
        writer.writerow([
            subscriber.email,
            subscriber.name,
            subscriber.language_preference,
            'Active' if subscriber.is_active else 'Inactive',
            subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response


@admin_required
@require_POST
def newsletter_subscriber_activate(request, subscriber_id):
    """Activate a newsletter subscriber."""
    subscriber = get_object_or_404(Newsletter, id=subscriber_id)
    subscriber.is_active = True
    subscriber.save()
    messages.success(request, 'Subscriber activated successfully.')
    return redirect('admin_panel:newsletter_list')


@admin_required
@require_POST
def newsletter_subscriber_deactivate(request, subscriber_id):
    """Deactivate a newsletter subscriber."""
    subscriber = get_object_or_404(Newsletter, id=subscriber_id)
    subscriber.is_active = False
    subscriber.save()
    messages.success(request, 'Subscriber deactivated successfully.')
    return redirect('admin_panel:newsletter_list')


@admin_required
@require_POST
def newsletter_subscriber_delete(request, subscriber_id):
    """Delete a newsletter subscriber."""
    subscriber = get_object_or_404(Newsletter, id=subscriber_id)
    subscriber.delete()
    messages.success(request, 'Subscriber deleted successfully.')
    return redirect('admin_panel:newsletter_list')


@admin_required
def newsletter_campaigns(request):
    """Display email campaigns."""
    campaigns = EmailCampaign.objects.all().order_by('-created_at')

    paginator = Paginator(campaigns, 20)
    page = request.GET.get('page')
    campaigns = paginator.get_page(page)

    context = {
        'campaigns': campaigns,
    }
    return render(request, 'admin_panel/newsletter/campaigns.html', context)


@admin_required
def newsletter_campaign_create(request):
    """Create a new email campaign."""
    from newsletter.forms import EmailCampaignForm

    if request.method == 'POST':
        form = EmailCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, 'Campaign created successfully.')
            return redirect('admin_panel:newsletter_campaigns')
    else:
        form = EmailCampaignForm()

    context = {
        'form': form,
    }
    return render(request, 'admin_panel/newsletter/campaign_edit.html', context)


@admin_required
def newsletter_campaign_edit(request, campaign_id):
    """Edit an email campaign."""
    from newsletter.forms import EmailCampaignForm

    campaign = get_object_or_404(EmailCampaign, id=campaign_id)

    if request.method == 'POST':
        form = EmailCampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, 'Campaign updated successfully.')
            return redirect('admin_panel:newsletter_campaigns')
    else:
        form = EmailCampaignForm(instance=campaign)

    context = {
        'form': form,
        'campaign': campaign,
    }
    return render(request, 'admin_panel/newsletter/campaign_edit.html', context)


@admin_required
@require_POST
def newsletter_campaign_delete(request, campaign_id):
    """Delete an email campaign."""
    campaign = get_object_or_404(EmailCampaign, id=campaign_id)
    campaign.delete()
    messages.success(request, 'Campaign deleted successfully.')
    return redirect('admin_panel:newsletter_campaigns')


@admin_required
def newsletter_campaign_send(request, campaign_id):
    """Send an email campaign."""
    campaign = get_object_or_404(EmailCampaign, id=campaign_id)

    if request.method == 'POST':
        # Logic to send campaign
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        messages.success(request, 'Campaign sent successfully.')
        return redirect('admin_panel:newsletter_campaigns')

    return redirect('admin_panel:newsletter_campaigns')


@admin_required
def chatbot_faqs(request):
    """Display chatbot FAQs."""
    faqs = ChatbotFAQ.objects.all().order_by('-created_at')

    paginator = Paginator(faqs, 20)
    page = request.GET.get('page')
    faqs = paginator.get_page(page)

    context = {
        'faqs': faqs,
    }
    return render(request, 'admin_panel/chatbot/faqs.html', context)


@admin_required
def chatbot_quick_responses(request):
    """Display chatbot quick responses."""
    responses = QuickResponse.objects.all().order_by('-created_at')

    paginator = Paginator(responses, 20)
    page = request.GET.get('page')
    responses = paginator.get_page(page)

    context = {
        'responses': responses,
    }
    return render(request, 'admin_panel/chatbot/quick_responses.html', context)


@admin_required
def chatbot_sessions(request):
    """Display chatbot sessions."""
    sessions = ChatSession.objects.all().order_by('-created_at')

    paginator = Paginator(sessions, 20)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)

    context = {
        'sessions': sessions,
    }
    return render(request, 'admin_panel/chatbot/sessions.html', context)


@admin_required
def chatbot_management(request):
    """Display chatbot management page."""
    return render(request, 'admin_panel/chatbot/management.html')


@admin_required
def notifications_list(request):
    """Display notifications."""
    return render(request, 'admin_panel/notifications.html')


@admin_required
@require_POST
def notification_mark_read(request, notification_id):
    """Mark a notification as read."""
    # Implementation depends on your notification model
    messages.success(request, 'Notification marked as read.')
    return redirect('admin_panel:notifications_list')


@admin_required
@require_POST
def notifications_mark_all_read(request):
    """Mark all notifications as read."""
    # Implementation depends on your notification model
    messages.success(request, 'All notifications marked as read.')
    return redirect('admin_panel:notifications_list')


@admin_required
def reports(request):
    """Display reports page."""
    return render(request, 'admin_panel/reports.html')


@admin_required
def analytics(request):
    """Display analytics dashboard."""
    return render(request, 'admin_panel/analytics.html')


@admin_required
def analytics_sales(request):
    """Display sales analytics."""
    return render(request, 'admin_panel/analytics_sales.html')


@admin_required
def analytics_customers(request):
    """Display customer analytics."""
    return render(request, 'admin_panel/analytics_customers.html')


@admin_required
def analytics_products(request):
    """Display product analytics."""
    return render(request, 'admin_panel/analytics_products.html')


@admin_required
def tax_settings(request):
    """Display tax settings page."""
    return render(request, 'admin_panel/tax_settings.html')


@admin_required
def customers_list(request):
    """Display list of customers."""
    customers = UserProfile.objects.select_related('user').order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/customers/list.html', context)


@admin_required
def customer_detail(request, customer_id):
    """Display customer details."""
    customer = get_object_or_404(UserProfile, id=customer_id)

    # Get customer orders
    orders = Order.objects.filter(user=customer.user).order_by('-created_at')
    orders_count = orders.count()
    total_spent = orders.filter(payment_status='completed').aggregate(
        total=Sum('total')
    )['total'] or 0

    context = {
        'customer': customer,
        'orders': orders[:10],  # Recent 10 orders
        'orders_count': orders_count,
        'total_spent': total_spent,
    }
    return render(request, 'admin_panel/customers/detail.html', context)


@admin_required
def customers_export(request):
    """Export customers to CSV."""
    customers = UserProfile.objects.select_related('user').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Date Joined', 'Orders Count'])

    for customer in customers:
        orders_count = Order.objects.filter(user=customer.user).count()
        writer.writerow([
            f"{customer.user.first_name} {customer.user.last_name}",
            customer.user.email,
            customer.phone,
            customer.created_at.strftime('%Y-%m-%d'),
            orders_count
        ])

    return response


@admin_required
def products_export(request):
    """Export products to CSV or PDF."""
    format_type = request.GET.get('format', 'csv')

    # Get filtered products
    products = Product.objects.all()

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if status_filter:
        if status_filter == 'active':
            products = products.filter(is_active=True)
        elif status_filter == 'inactive':
            products = products.filter(is_active=False)

    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'SKU', 'Category', 'Price', 'Stock', 'Status', 'Created At'
        ])

        for product in products:
            writer.writerow([
                product.name,
                product.sku,
                product.category.name if product.category else '',
                product.price,
                product.stock_quantity,
                'Active' if product.is_active else 'Inactive',
                product.created_at.strftime('%Y-%m-%d')
            ])

        return response

    elif format_type == 'pdf':
        # For PDF export, we'll use a simple HTML response
        html = f"""
        <html>
        <head><title>Products Report</title></head>
        <body>
            <h1>Products Report</h1>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>SKU</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
        """

        for product in products:
            html += f"""
                    <tr>
                        <td>{product.name}</td>
                        <td>{product.sku}</td>
                        <td>{product.category.name if product.category else ''}</td>
                        <td>{product.price}</td>
                        <td>{product.stock_quantity}</td>
                        <td>{'Active' if product.is_active else 'Inactive'}</td>
                        <td>{product.created_at.strftime('%Y-%m-%d')}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="products.html"'
        return response

    return redirect('admin_panel:products_list')


@admin_required
@require_POST
def products_bulk_update(request):
    """Bulk update products."""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return JsonResponse({'error': 'No products selected'}, status=400)

        products = Product.objects.filter(id__in=product_ids)

        if action == 'activate':
            products.update(is_active=True)
            message = f'{products.count()} products activated successfully'
        elif action == 'deactivate':
            products.update(is_active=False)
            message = f'{products.count()} products deactivated successfully'
        elif action == 'delete':
            count = products.count()
            products.delete()
            message = f'{count} products deleted successfully'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error in products bulk update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@require_POST
def send_customer_email(request):
    """Send email to customer."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([email, subject, message]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@admin_required
def orders_list(request):
    """Display list of orders with filtering and search."""
    orders = Order.objects.select_related('user').order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(billing_first_name__icontains=search_query) |
            Q(billing_last_name__icontains=search_query) |
            Q(billing_email__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(payment_status=status_filter)

    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        if date_filter == 'today':
            orders = orders.filter(created_at__date=timezone.now().date())
        elif date_filter == 'week':
            start_date = timezone.now() - timedelta(days=7)
            orders = orders.filter(created_at__gte=start_date)
        elif date_filter == 'month':
            start_date = timezone.now() - timedelta(days=30)
            orders = orders.filter(created_at__gte=start_date)

    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin_panel/orders/list.html', context)


@admin_required
@require_POST
@csrf_exempt
def orders_bulk_action(request):
    """Handle bulk actions on orders with admin password confirmation."""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        order_ids = data.get('order_ids', [])
        admin_password = data.get('admin_password')

        logger.info(f"Bulk action request received: action={action}, order_ids={order_ids}")

        # Verify admin password
        user = authenticate(username=request.user.username, password=admin_password)
        if user is None or not user.is_staff:
            logger.warning("Invalid admin password for bulk action")
            return JsonResponse({'error': 'Invalid admin password.'}, status=403)

        orders = Order.objects.filter(id__in=order_ids)

        if action == 'delete':
            count, _ = orders.delete()
            logger.info(f"Deleted {count} orders")
            return JsonResponse({'success': True, 'message': f'{count} orders deleted.'})

        elif action == 'update_status':
            new_status = data.get('new_status')
            if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
                logger.warning(f"Invalid status value: {new_status}")
                return JsonResponse({'error': 'Invalid status value.'}, status=400)
            orders.update(status=new_status)
            logger.info("Order status updated")
            return JsonResponse({'success': True, 'message': 'Order status updated.'})

        elif action == 'update_payment':
            new_payment_status = data.get('new_payment_status')
            if new_payment_status not in ['pending', 'paid', 'failed']:
                logger.warning(f"Invalid payment status value: {new_payment_status}")
                return JsonResponse({'error': 'Invalid payment status value.'}, status=400)
            orders.update(payment_status=new_payment_status)
            logger.info("Payment status updated")
            return JsonResponse({'success': True, 'message': 'Payment status updated.'})

        else:
            logger.warning(f"Invalid action: {action}")
            return JsonResponse({'error': 'Invalid action.'}, status=400)

    except Exception as e:
        logger.error(f"Error in bulk action: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        if date_filter == 'today':
            orders = orders.filter(created_at__date=timezone.now().date())
        elif date_filter == 'week':
            start_date = timezone.now() - timedelta(days=7)
            orders = orders.filter(created_at__gte=start_date)
        elif date_filter == 'month':
            start_date = timezone.now() - timedelta(days=30)
            orders = orders.filter(created_at__gte=start_date)

    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin_panel/orders/list.html', context)


@admin_required
def order_detail(request, order_id):
    """Display detailed information about a specific order."""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product')

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'admin_panel/orders/detail.html', context)


@admin_required
def order_invoice(request, order_id):
    """Generate PDF invoice for an order."""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product')

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'admin_panel/orders/invoice.html', context)


from cart.utils.pdf import render_to_pdf
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@admin_required
def send_invoice_email(request, order_id):
    """Send invoice email to customer."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        order = get_object_or_404(Order, id=order_id)

        # Generate invoice PDF using xhtml2pdf utility
        context = {
            'order': order,
            'order_items': order.items.all(),
            'request': request,
        }
        pdf_response = render_to_pdf('admin_panel/orders/invoice.html', context)

        if pdf_response:
            pdf_content = pdf_response.content
        else:
            return JsonResponse({'error': 'Failed to generate PDF'}, status=500)

        # Send email
        subject = f'Invoice for Order #{order.order_number}'
        message = f'Dear {order.billing_first_name},\n\nPlease find attached your invoice for order #{order.order_number}.\n\nThank you for shopping with CareCove!'

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.billing_email]
        )
        email.attach(f'invoice_{order.order_number}.pdf', pdf_content, 'application/pdf')
        email.send()

        messages.success(request, f'Invoice email sent to {order.billing_email}')
        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f'Error sending invoice email: {str(e)}')
        return JsonResponse({'error': 'Failed to send invoice email'}, status=500)


@admin_required
def orders_export(request):
    """Export orders to CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order Number',
        'Date',
        'Customer',
        'Email',
        'Total',
        'Payment Status',
        'Payment Method',
        'Shipping Address',
        'Billing Address'
    ])

    orders = Order.objects.select_related('user').order_by('-created_at')

    for order in orders:
        writer.writerow([
            order.order_number,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            f"{order.billing_first_name} {order.billing_last_name}",
            order.billing_email,
            order.total,
            order.payment_status,
            order.payment_method,
            f"{order.shipping_address_1}, {order.shipping_city}, {order.shipping_country}",
            f"{order.billing_address_1}, {order.billing_city}, {order.billing_country}"
        ])

    return response


@admin_required
def order_update_status(request, order_id):
    """Update order status and notes."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        order = get_object_or_404(Order, id=order_id)

        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status:
            order.payment_status = new_status
            order.save()

        if notes:
            order.notes = notes
            order.save()

        messages.success(request, f'Order #{order.order_number} updated successfully')
        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f'Error updating order: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)