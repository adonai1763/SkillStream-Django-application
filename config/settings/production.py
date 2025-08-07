"""
Production settings for SkillStream project.

This file contains settings specific to the production environment.
"""

import os
from .base import *
import cloudinary
import cloudinary.uploader
import cloudinary.api

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow deployment hosts - will be configured based on platform
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    '.up.railway.app',  # Railway subdomains
    '.onrender.com',    # Render subdomains
    '.vercel.app',      # Vercel subdomains
    '.herokuapp.com',   # Heroku subdomains
]

# Add custom domain from environment variable if provided
if os.environ.get('ALLOWED_HOST'):
    ALLOWED_HOSTS.append(os.environ.get('ALLOWED_HOST'))

# Database - Use PostgreSQL if available, fallback to SQLite
import dj_database_url

# Try DATABASE_URL first (PostgreSQL), fallback to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite for quick deployment
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration for production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Only enforce HTTPS if we have SSL (Render provides this automatically)
SECURE_SSL_REDIRECT = False  # Render handles this at the load balancer level
SESSION_COOKIE_SECURE = False  # Set to True if you have HTTPS working
CSRF_COOKIE_SECURE = False     # Set to True if you have HTTPS working

# Cloudinary configuration for video storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dlj95n6hw'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '221561824591952'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'mNL_KXBRKymAUFW4456QYJGaKKk'),
}

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# Use Cloudinary for media file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Production logging - console only (Render captures this)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}