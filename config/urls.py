"""
URL configuration for SkillStream project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Admin site customization
admin.site.site_header = "SkillStream Administration"
admin.site.site_title = "SkillStream Admin"
admin.site.index_title = "Welcome to SkillStream Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve media files in all environments
# Note: In production, consider using cloud storage (AWS S3, Cloudinary)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development only (WhiteNoise handles production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Healthcheck routes
urlpatterns += [
    path('health/', lambda request: HttpResponse("OK")),
]
