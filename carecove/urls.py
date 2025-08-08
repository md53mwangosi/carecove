
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check, simple_health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('admin_panel.urls')),
    path('', include('shop.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('chatbot/', include('chatbot.urls')),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/simple/', simple_health_check, name='simple_health_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
