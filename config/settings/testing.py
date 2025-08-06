"""
Testing settings for SkillStream project.

This file contains settings specific to running tests.
Optimized for speed and isolation.
"""

from .base import *

# Use a simple secret key for testing
SECRET_KEY = 'test-secret-key-not-for-production'

# Debug should be False for testing to catch template errors
DEBUG = False

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use local memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Password hashers - use faster hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Media files for testing
MEDIA_ROOT = '/tmp/skillstream_test_media'

# Static files for testing
STATIC_ROOT = '/tmp/skillstream_test_static'

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Disable CSRF for API testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False