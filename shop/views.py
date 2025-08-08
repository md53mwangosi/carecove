from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.core.mail import mail_admins
from .models import Product, Category, ProductReview
from .forms import ContactForm, ProductReviewForm

def home(request):
    """Homepage with all products prominently displayed."""
    # Get all active products, featuring important ones first
    all_products = Product.objects.filter(is_active=True).order_by('-is_featured', '-created_at')[:12]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    categories = Category.objects.filter(is_active=True)[:4]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    
    context = {
        'all_products': all_products,
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    """Product listing with filtering and search."""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    product_type = request.GET.get('type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'name')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if product_type:
        products = products.filter(product_type=product_type)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_slug': category_slug,
        'product_type': product_type,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    """Product detail page with reviews."""
    product = get_object_or_404(Product, slug=slug)
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Check if user can review
    user_can_review = False
    if request.user.is_authenticated:
        user_can_review = not ProductReview.objects.filter(
            product=product, 
            user=request.user
        ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'user_can_review': user_can_review,
    }
    return render(request, 'shop/product_detail.html', context)

def category_detail(request, slug):
    """Category detail page."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'shop/category_detail.html', context)

def search(request):
    """Search products."""
    search_query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(benefits__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'shop/search.html', context)

def about(request):
    """About page."""
    return render(request, 'shop/about.html')

def contact(request):
    """Contact page with form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email to admins
            try:
                mail_admins(
                    'Contact Form Submission',
                    f'Name: {form.cleaned_data["name"]}\n'
                    f'Email: {form.cleaned_data["email"]}\n'
                    f'Message: {form.cleaned_data["message"]}',
                    fail_silently=True,
                )
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
            except Exception:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
            return redirect('shop:contact')
    else:
        form = ContactForm()
    
    return render(request, 'shop/contact.html', {'form': form})

@login_required
def submit_review(request, slug):
    """Submit a product review with admin notification."""
    product = get_object_or_404(Product, slug=slug)
    
    # Check if user has already reviewed this product
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('shop:product_detail', slug=slug)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False  # Ensure new reviews are pending approval
            review.save()
            
            # Send notification to admins
            try:
                mail_admins(
                    f'New Review for {product.name} - Pending Approval',
                    f'A new product review has been submitted:\n\n'
                    f'Product: {product.name}\n'
                    f'User: {request.user.username} ({request.user.email})\n'
                    f'Rating: {review.rating} stars\n'
                    f'Title: {review.title}\n'
                    f'Review: {review.review[:300]}...\n\n'
                    f'Please review and approve/reject this review in the admin panel.\n\n'
                    f'Admin URL: {request.build_absolute_uri("/admin/shop/productreview/")}',
                    fail_silently=True,
                )
            except Exception:
                pass  # Fail silently if email can't be sent
            
            messages.success(request, 'Thank you for your review! It will be published after approval.')
            return redirect('shop:product_detail', slug=slug)
    else:
        form = ProductReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'shop/submit_review.html', context)