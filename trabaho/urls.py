"""
URL configuration for trabaho project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from jobs.error_handlers import page_not_found, server_error, bad_request, permission_denied

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('jobs.api_urls')),  # REST Framework API endpoints
    path('', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = bad_request
handler403 = permission_denied
handler404 = page_not_found
handler500 = server_error

