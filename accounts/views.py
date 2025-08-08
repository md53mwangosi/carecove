
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Address
from .forms import UserProfileForm, AddressForm
from cart.models import Order

def register(request):
    """User registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('shop:home')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    """User profile page."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def order_history(request):
    """User order history."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {'orders': orders}
    return render(request, 'accounts/order_history.html', context)

@login_required
def manage_addresses(request):
    """Manage user addresses."""
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:manage_addresses')
    else:
        form = AddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'accounts/manage_addresses.html', context)

def logout_view(request):
    """Custom logout view."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('shop:home')
