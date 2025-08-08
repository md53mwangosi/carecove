from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
import os
import logging
import json
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
from .pesapal import PesapalService
from shop.models import Product, ProductVariant

logger = logging.getLogger(__name__)



def cart_detail(request):
    """Display the shopping cart."""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
    }
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def add_to_cart(request):
    """Add a product to the cart."""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
    
    cart = get_or_create_cart(request)
    
    # Check if item already exists in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_total': cart.total_price,
            'cart_items': cart.total_items
        })
    
    messages.success(request, 'Product added to cart!')
    return redirect('cart:cart_detail')

@require_POST
def update_cart(request):
    """Update cart item quantity."""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    
    # Ensure cart belongs to current user/session
    if request.user.is_authenticated:
        if cart.user != request.user:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    else:
        if cart.session_key != request.session.session_key:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    cart = get_or_create_cart(request)  # Refresh cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_price,
            'cart_items': cart.total_items
        })
    
    return redirect('cart:cart_detail')

@require_POST
def remove_from_cart(request):
    """Remove item from cart."""
    item_id = request.POST.get('item_id')
    
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    
    # Ensure cart belongs to current user/session
    if request.user.is_authenticated:
        if cart.user != request.user:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    else:
        if cart.session_key != request.session.session_key:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = get_or_create_cart(request)
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_total': cart.total_price,
            'cart_items': cart.total_items
        })
    
    messages.success(request, 'Item removed from cart!')
    return redirect('cart:cart_detail')

def checkout(request):
    """Display checkout form."""
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:home')
    
    form = CheckoutForm()
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'cart/checkout.html', context)

def pre_payment_invoice(request, order_id):
    """Display pre-payment invoice."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has access to this order
    if request.user.is_authenticated and order.user != request.user:
        messages.error(request, 'You do not have access to this order.')
        return redirect('shop:home')
    
    # Check session for guest users
    if not request.user.is_authenticated:
        last_order_id = request.session.get('last_order_id')
        if str(order.id) != last_order_id:
            messages.error(request, 'You do not have access to this order.')
            return redirect('shop:home')
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'cart/pre_payment_invoice.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from cart.utils.pdf import render_to_pdf

@login_required
def download_pre_payment_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Check access
    if not (request.user.is_staff or order.user == request.user):
        return redirect('shop:home')

    context = {
        'order': order,
        'order_items': order.items.all(),
        'request': request,
    }

    pdf_response = render_to_pdf('cart/pre_payment_invoice.html', context)
    if pdf_response:
        pdf_response['Content-Disposition'] = f'attachment; filename=pre_payment_invoice_{order.order_number}.pdf'
        return pdf_response
    else:
        return HttpResponse('We had some errors while generating the PDF')

def process_payment(request):
    """Process payment with Pesapal."""
    import json
    logger.info(f"process_payment called with POST data: {json.dumps(request.POST)}")

    if request.method != "POST":
        messages.error(request, 'Method Not Allowed')
        return redirect('cart:checkout')

    order_id = request.POST.get('order_id')
    if not order_id:
        logger.error('process_payment called without order_id in POST data')
        messages.error(request, 'Missing order ID')
        return redirect('cart:checkout')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} not found in process_payment')
        messages.error(request, 'Order not found')
        return redirect('cart:checkout')

    # Check access
    if request.user.is_authenticated and order.user != request.user:
        messages.error(request, 'Unauthorized')
        return redirect('cart:checkout')

    if not request.user.is_authenticated:
        last_order_id = request.session.get('last_order_id')
        if str(order.id) != last_order_id:
            messages.error(request, 'Unauthorized')
            return redirect('cart:checkout')

    try:
        pesapal = PesapalService()

        # Prepare payment data
        callback_url = request.build_absolute_uri(
            reverse('cart:pesapal_callback', args=[order.order_number])
        )

        ipn_id = settings.PESAPAL_IPN_ID
        logger.debug(f"Using Pesapal IPN ID: {ipn_id}")

        # Create order items for Pesapal
        order_items = []
        for item in order.items.all():
            order_items.append({
                'item': item.product.name,
                'quantity': str(item.quantity),
                'unit_cost': str(item.price),
                'subtotal': str(item.total)
            })

        # Submit payment request
        response_data = pesapal.submit_order(
            order_id=order.order_number,
            currency='TZS',
            amount=str(order.total),
            description=f'Order {order.order_number} - CareCove Sea Moss',
            callback_url=callback_url,
            notification_url=ipn_id,
            billing_email=order.email,
            billing_phone=order.billing_phone,
            billing_first_name=order.billing_first_name,
            billing_last_name=order.billing_last_name,
            line_items=order_items
        )

        logger.info(f'Pesapal submit_order response: {response_data}')

        if response_data.get('status') == '200':
            # Update order with Pesapal tracking ID
            order_tracking_id = response_data.get('order_tracking_id')
            if order_tracking_id:
                order.pesapal_order_tracking_id = order_tracking_id
                order.save()
            else:
                logger.error(f"Pesapal submit_order returned no order_tracking_id for order {order.order_number}")

            # Redirect to Pesapal payment page
            redirect_url = response_data.get('redirect_url')
            if redirect_url:
                return redirect(redirect_url)
            else:
                messages.error(request, 'Payment processing failed: No redirect URL provided')
                return redirect('cart:checkout')
        else:
            logger.error(f"Pesapal submit_order failed for order {order_id}: {response_data}")
            error_message = response_data.get('error', 'Payment processing failed')
            messages.error(request, f"Payment processing failed: {error_message}")
            return redirect('cart:checkout')

    except Exception as e:
        logger.error(f"Error processing payment for order {order_id}: {str(e)}")
        messages.error(request, 'Payment processing failed. Please try again.')
        return redirect('cart:checkout')

def payment_success(request):
    """Display payment success page."""
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'Invalid order ID.')
        return redirect('shop:home')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')

    # Clear cart after successful payment
    try:
        cart = get_or_create_cart(request)
        cart.items.all().delete()

        # Clear session
        if 'last_order_id' in request.session:
            del request.session['last_order_id']
    except:
        pass

    context = {
        'order': order,
    }
    return render(request, 'cart/payment_success.html', context)

def payment_failed(request):
    """Display payment failed page."""
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'Invalid order ID.')
        return redirect('shop:home')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')

    context = {
        'order': order,
    }
    return render(request, 'cart/payment_failed.html', context)

def send_order_confirmation_email(order):
    """Send order confirmation email after successful payment."""
    try:
        subject = f"Order Confirmation #{order.order_number} - CareCove Sea Moss"
        html_message = render_to_string('cart/order_confirmation_email.html', {
            'order': order,
            'customer_name': f"{order.billing_first_name} {order.billing_last_name}",
        })

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.content_subtype = 'html'
        email.send()

    except Exception as e:
        logger.error(f"Error sending order confirmation email: {str(e)}")

def checkout_confirm(request):
    """Handle checkout form submission and create pending order."""
    cart = get_or_create_cart(request)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Calculate totals
            subtotal = cart.total_price
            shipping_cost = 5000 if subtotal < 50000 else 0  # Free shipping over 50,000 TSH
            tax_amount = 0  # No tax for now
            total = subtotal + shipping_cost + tax_amount

            # Create pending order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=form.cleaned_data['email'],
                billing_first_name=form.cleaned_data['billing_first_name'],
                billing_last_name=form.cleaned_data['billing_last_name'],
                billing_company=form.cleaned_data.get('billing_company', ''),
                billing_address_1=form.cleaned_data['billing_address_1'],
                billing_address_2=form.cleaned_data.get('billing_address_2', ''),
                billing_city=form.cleaned_data['billing_city'],
                billing_state=form.cleaned_data['billing_state'],
                billing_postal_code=form.cleaned_data['billing_postal_code'],
                billing_country=form.cleaned_data.get('billing_country', 'Tanzania'),
                billing_phone=form.cleaned_data['billing_phone'],
                shipping_first_name=form.cleaned_data.get('shipping_first_name', form.cleaned_data['billing_first_name']),
                shipping_last_name=form.cleaned_data.get('shipping_last_name', form.cleaned_data['billing_last_name']),
                shipping_company=form.cleaned_data.get('shipping_company', ''),
                shipping_address_1=form.cleaned_data.get('shipping_address_1', form.cleaned_data['billing_address_1']),
                shipping_address_2=form.cleaned_data.get('shipping_address_2', ''),
                shipping_city=form.cleaned_data.get('shipping_city', form.cleaned_data['billing_city']),
                shipping_state=form.cleaned_data.get('shipping_state', form.cleaned_data['billing_state']),
                shipping_postal_code=form.cleaned_data.get('shipping_postal_code', form.cleaned_data['billing_postal_code']),
                shipping_country=form.cleaned_data.get('shipping_country', 'Tanzania'),
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total=total,
                order_notes=form.cleaned_data.get('order_notes', ''),
                payment_status='pending',
                status='pending'
            )

            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    total=cart_item.total_price,
                )

            # Store order ID in session for guest access
            request.session['last_order_id'] = str(order.id)

            # Send invoice email immediately
            try:
                send_order_invoice_email(order)
                messages.success(request, 'Invoice created! Check your email for the invoice.')
            except Exception as e:
                messages.warning(request, 'Invoice created! You can download it below.')

            # Redirect to pre-payment invoice
            return redirect('cart:pre_payment_invoice', order_id=order.id)

    # If GET request or form invalid, redirect to checkout
    return redirect('cart:checkout')

def order_detail(request, order_id):
    """Display order detail for customer."""
    order = get_object_or_404(Order, id=order_id)

    # Check access
    if request.user.is_authenticated and order.user != request.user:
        messages.error(request, 'You do not have access to this order.')
        return redirect('shop:home')

    if not request.user.is_authenticated:
        last_order_id = request.session.get('last_order_id')
        if str(order.id) != last_order_id:
            messages.error(request, 'You do not have access to this order.')
            return redirect('shop:home')

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'cart/order_detail.html', context)

@login_required
def customer_invoice(request, order_id):
    """Display customer invoice using the admin panel invoice template."""
    order = get_object_or_404(Order, id=order_id)

    # Check access
    if request.user.is_authenticated and order.user != request.user:
        return redirect('shop:home')

    if not request.user.is_authenticated:
        last_order_id = request.session.get('last_order_id')
        if str(order.id) != last_order_id:
            return redirect('shop:home')

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'admin_panel/orders/invoice.html', context)

@csrf_exempt
def pesapal_callback(request, order_number):
    """Handle Pesapal callback after payment."""
    order = get_object_or_404(Order, order_number=order_number)

    transaction_id = request.GET.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference')

    logger.info(f"Pesapal callback received: transaction_id={transaction_id}, merchant_reference={merchant_reference}, order_number={order_number}")

    if transaction_id and merchant_reference == order.order_number:
        try:
            pesapal = PesapalService()
            transaction_status = pesapal.get_transaction_status(transaction_id)

            logger.info(f"Transaction status response: {transaction_status}")

            if transaction_status:
                # Extract actual payment status
                payment_status_description = transaction_status.get('payment_status_description', '').upper()
                status_code = transaction_status.get('status_code')
                description = transaction_status.get('description', '').upper()

                logger.info(f"Payment status description: {payment_status_description}, status_code: {status_code}, description: {description}")

                # Determine success vs failure based on actual payment indicators
                is_successful = False

                # Check payment status description
                if 'COMPLETED' in payment_status_description or 'SUCCESS' in payment_status_description:
                    is_successful = True
                elif 'FAILED' in payment_status_description or 'CANCELLED' in payment_status_description:
                    is_successful = False
                elif 'PENDING' in payment_status_description:
                    is_successful = False  # Treat pending as failed for now
                else:
                    # Check description for success indicators
                    if 'SUCCESS' in description or 'COMPLETED' in description:
                        is_successful = True
                    elif 'FAILED' in description or 'CANCELLED' in description or 'UNABLE TO AUTHORIZE' in description:
                        is_successful = False
                    else:
                        # Default to checking status_code
                        is_successful = str(status_code) == '1' and 'FAILED' not in description

                logger.info(f"Payment considered successful: {is_successful}")

                if is_successful:
                    order.payment_status = 'completed'
                    order.status = 'confirmed'  # Changed from 'processing' to 'confirmed'
                    order.pesapal_order_tracking_id = transaction_id
                    order.save()

                    # Send confirmation email
                    try:
                        send_order_confirmation_email(order)
                    except Exception as e:
                        logger.error(f"Error sending confirmation email: {str(e)}")

                    messages.success(request, f'Payment successful! Order #{order.order_number} has been placed.')
                    return redirect(f'/cart/payment-success/?order_id={order.id}')
                else:
                    logger.warning(f"Payment failed with status: {payment_status_description}, description: {description}")
                    order.payment_status = 'failed'
                    order.status = 'cancelled'
                    order.save()
                    messages.error(request, f'Payment failed for order #{order.order_number}. Reason: {payment_status_description}')
                    return redirect(f'/cart/payment-failed/?order_id={order.id}')

        except Exception as e:
            logger.error(f"Error processing Pesapal callback: {str(e)}")
            messages.error(request, 'Error processing payment. Please try again.')

    logger.warning("Pesapal callback failed - missing parameters or mismatch")
    messages.error(request, 'Payment processing failed. Please contact support.')
    return redirect('cart:payment_failed')

@csrf_exempt
def pesapal_ipn(request):
    """Handle Pesapal IPN (Instant Payment Notification)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_tracking_id = data.get('OrderTrackingId')
            order_merchant_reference = data.get('OrderMerchantReference')
            
            if order_tracking_id and order_merchant_reference:
                order = get_object_or_404(Order, order_number=order_merchant_reference)
                
                pesapal = PesapalService()
                transaction_status = pesapal.get_transaction_status(order_tracking_id)
                
                if transaction_status.get('status') == '200':
                    payment_status = transaction_status.get('payment_status', {}).get('status_code')
                    
                    if payment_status == '200':
                        order.payment_status = 'completed'
                        order.pesapal_order_tracking_id = order_tracking_id
                        order.save()
                        
                        # Send confirmation email
                        try:
                            send_order_confirmation_email(order)
                        except Exception as e:
                            logger.error(f"Error sending confirmation email: {str(e)}")
                
                return JsonResponse({'status': 'success'})
                
        except Exception as e:
            logger.error(f"Error processing IPN: {str(e)}")
    
    return JsonResponse({'status': 'error'})

def send_order_confirmation_email(order):
    """Send order confirmation email after successful payment."""
    try:
        subject = f"Order Confirmation #{order.order_number} - CareCove Sea Moss"
        html_message = render_to_string('cart/order_confirmation_email.html', {
            'order': order,
            'customer_name': f"{order.billing_first_name} {order.billing_last_name}",
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.content_subtype = 'html'
        email.send()
        
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {str(e)}")

# Helper function to get or create cart
def get_or_create_cart(request):
    """Get or create cart for current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def send_order_invoice_email(order):
    """Send invoice email to customer after order creation."""
    try:
        # Generate PDF invoice
        pdf_buffer = generate_invoice_pdf(order)

        # Prepare email
        subject = f"Invoice #{order.order_number} - CareCove Sea Moss"
        html_message = render_to_string('admin_panel/orders/invoice_email.html', {
            'order': order,
            'customer_name': f"{order.billing_first_name} {order.billing_last_name}",
        })

        # Create email
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.content_subtype = 'html'

        # Attach PDF
        email.attach(f'invoice_{order.order_number}.pdf', pdf_buffer.getvalue(), 'application/pdf')

        # Send email
        email.send()

        return True

    except Exception as e:
        logger.error(f"Error sending invoice email for order {order.id}: {str(e)}")
        return False

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import logging

from cart.utils.pdf import render_to_pdf

@login_required
def download_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Allow access if user is owner or staff
    if not (request.user.is_staff or order.user == request.user):
        return redirect('shop:home')

    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items,
        'request': request,
    }

    pdf_response = render_to_pdf('admin_panel/orders/invoice.html', context)
    if pdf_response:
        pdf_response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_number}.pdf'
        return pdf_response
    else:
        return HttpResponse('We had some errors while generating the PDF')