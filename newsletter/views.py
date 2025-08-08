import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Newsletter
from .forms import NewsletterForm

logger = logging.getLogger(__name__)

def subscribe(request):
    debug_info = {}

    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                name = form.cleaned_data.get('name', '')
                language_preference = form.cleaned_data.get('language_preference', 'en')

                # Create subscription
                Newsletter.objects.create(
                    email=email,
                    name=name,
                    language_preference=language_preference,
                    is_pending_approval=True,
                    is_active=False
                )

                messages.success(request, 'Thank you for subscribing! Please check your email for confirmation.')
                return redirect('newsletter:subscription_thank_you')

            except Exception as e:
                logger.error(f"Newsletter subscription error: {str(e)}")
                messages.error(request, 'An error occurred. Please try again.')
        else:
            debug_info['form_errors'] = form.errors
    else:
        form = NewsletterForm()

    return render(request, 'newsletter/subscribe.html', {
        'form': form,
        'debug_info': debug_info
    })

def unsubscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                subscriber = Newsletter.objects.get(email__iexact=email)
                subscriber.is_active = False
                subscriber.unsubscribed_at = timezone.now()
                subscriber.save()
                messages.success(request, 'You have been successfully unsubscribed.')
            except Newsletter.DoesNotExist:
                messages.error(request, 'Email not found in our subscription list.')
        else:
            messages.error(request, 'Please provide an email address.')

    email = request.GET.get('email', '')
    return render(request, 'newsletter/unsubscribe.html', {'email': email})

def subscription_thank_you(request):
    return render(request, 'newsletter/subscription_thank_you.html')