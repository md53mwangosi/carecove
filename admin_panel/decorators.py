
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from functools import wraps

def admin_required(function=None, redirect_url='/accounts/login/'):
    """
    Decorator to require admin privileges
    """
    def check_admin(user):
        return user.is_authenticated and (user.is_staff or user.is_superuser)
    
    actual_decorator = user_passes_test(check_admin, login_url=redirect_url)
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def ajax_required(function):
    """
    Decorator to require AJAX requests
    """
    @wraps(function)
    def wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return function(request, *args, **kwargs)
    return wrapped_view

def log_admin_action(action, model_name, object_id=None, description=None):
    """
    Decorator to log admin actions
    """
    def decorator(function):
        @wraps(function)
        def wrapped_view(request, *args, **kwargs):
            from .models import AdminActivityLog
            
            # Execute the view
            response = function(request, *args, **kwargs)
            
            # Log the action if successful
            if hasattr(response, 'status_code') and response.status_code < 400:
                AdminActivityLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    object_id=str(object_id) if object_id else '',
                    description=description or f'{action} {model_name}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            
            return response
        return wrapped_view
    return decorator
