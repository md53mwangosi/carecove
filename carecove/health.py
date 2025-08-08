
"""
Health check views for monitoring application status.
"""

from django.http import JsonResponse
from django.db import connections
from django.core.cache import cache
from django.conf import settings
import time
import os


def health_check(request):
    """
    Comprehensive health check endpoint.
    
    Returns:
        JSON response with health status and system information
    """
    health_data = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'version': '1.0.0',
        'environment': 'production' if not settings.DEBUG else 'development',
        'checks': {}
    }
    
    # Database health check
    try:
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_data['status'] = 'unhealthy'
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Cache health check (if Redis is configured)
    try:
        if hasattr(settings, 'CACHES') and 'redis' in str(settings.CACHES.get('default', {})):
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_data['checks']['cache'] = {'status': 'healthy'}
            else:
                raise Exception("Cache value mismatch")
        else:
            health_data['checks']['cache'] = {'status': 'not_configured'}
    except Exception as e:
        health_data['status'] = 'unhealthy'
        health_data['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Disk space check
    try:
        statvfs = os.statvfs('.')
        free_space = statvfs.f_frsize * statvfs.f_avail
        total_space = statvfs.f_frsize * statvfs.f_blocks
        usage_percent = ((total_space - free_space) / total_space) * 100
        
        if usage_percent > 90:
            health_data['status'] = 'unhealthy'
            health_data['checks']['disk'] = {
                'status': 'unhealthy',
                'usage_percent': round(usage_percent, 2),
                'message': 'Disk usage above 90%'
            }
        else:
            health_data['checks']['disk'] = {
                'status': 'healthy',
                'usage_percent': round(usage_percent, 2)
            }
    except Exception as e:
        health_data['checks']['disk'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    # Application-specific checks
    try:
        # Check if static files are accessible
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            health_data['checks']['static_files'] = {'status': 'healthy'}
        else:
            health_data['checks']['static_files'] = {'status': 'warning', 'message': 'Static files not collected'}
        
        # Check if media directory exists
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            health_data['checks']['media_files'] = {'status': 'healthy'}
        else:
            health_data['checks']['media_files'] = {'status': 'warning', 'message': 'Media directory not found'}
            
    except Exception as e:
        health_data['checks']['application'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Set HTTP status code based on overall health
    status_code = 200 if health_data['status'] == 'healthy' else 503
    
    return JsonResponse(health_data, status=status_code)


def simple_health_check(request):
    """
    Simple health check for load balancers.
    
    Returns:
        Plain text response for basic health monitoring
    """
    try:
        # Quick database check
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({'status': 'ok'}, status=200)
    except Exception:
        return JsonResponse({'status': 'error'}, status=503)
