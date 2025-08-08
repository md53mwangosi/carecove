
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Testimonial
from .forms import TestimonialForm

def testimonials_list(request):
    """Display approved testimonials."""
    testimonials = Testimonial.objects.filter(status='approved').order_by('-created_at')
    featured_testimonials = testimonials.filter(is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(testimonials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'featured_testimonials': featured_testimonials,
        'page_obj': page_obj,
    }
    return render(request, 'testimonials/testimonials_list.html', context)

def submit_testimonial(request):
    """Submit a new testimonial."""
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save(commit=False)
            if request.user.is_authenticated:
                testimonial.user = request.user
                if not testimonial.name:
                    testimonial.name = f"{request.user.first_name} {request.user.last_name}".strip()
                if not testimonial.email:
                    testimonial.email = request.user.email
            testimonial.save()
            return redirect('testimonials:testimonial_thank_you')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
            }
        form = TestimonialForm(initial=initial_data)
    
    context = {'form': form}
    return render(request, 'testimonials/submit_testimonial.html', context)

def testimonial_thank_you(request):
    """Thank you page after testimonial submission."""
    return render(request, 'testimonials/testimonial_thank_you.html')
