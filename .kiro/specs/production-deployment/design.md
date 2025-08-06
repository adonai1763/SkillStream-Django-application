# Design Document

## Overview

This design outlines the comprehensive deployment strategy for the SkillStream Django application to production environments, specifically targeting Heroku as the primary platform with additional cloud service integrations. The design focuses on demonstrating professional-level deployment skills, modern DevOps practices, and production-ready configurations that showcase technical competency to potential employers.

## Architecture

### Production Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Local Development]
        GIT[Git Repository]
    end
    
    subgraph "CI/CD Pipeline"
        GHA[GitHub Actions]
        TEST[Automated Tests]
        BUILD[Build Process]
    end
    
    subgraph "Heroku Production Environment"
        APP[Heroku App]
        DB[(PostgreSQL)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "External Services"
        S3[AWS S3 Storage]
        CDN[CloudFront CDN]
        MONITOR[Monitoring Service]
    end
    
    subgraph "Users"
        WEB[Web Users]
        MOBILE[Mobile Users]
    end
    
    DEV --> GIT
    GIT --> GHA
    GHA --> TEST
    TEST --> BUILD
    BUILD --> APP
    APP --> DB
    APP --> REDIS
    APP --> S3
    S3 --> CDN
    CDN --> WEB
    CDN --> MOBILE
    APP --> MONITOR
```

### Technology Stack for Production

**Platform**: Heroku (Primary deployment target)
**Database**: PostgreSQL (Heroku Postgres addon)
**Caching**: Redis (Heroku Redis addon)
**File Storage**: AWS S3 (for media files)
**CDN**: AWS CloudFront (for static/media delivery)
**CI/CD**: GitHub Actions
**Monitoring**: Heroku Metrics + Sentry
**SSL**: Heroku Automated Certificate Management

## Components and Interfaces

### 1. Heroku Application Configuration

**Procfile Configuration**
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
worker: python manage.py rqworker default (optional for background tasks)
```

**Runtime Configuration**
```
# runtime.txt
python-3.9.18
```

**Environment Variables**
```bash
# Core Django Settings
SECRET_KEY=<generated-secret-key>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DATABASE_URL=<heroku-postgres-url>

# Security
ALLOWED_HOSTS=skillstream-app.herokuapp.com,www.skillstream-app.herokuapp.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=<aws-access-key>
AWS_SECRET_ACCESS_KEY=<aws-secret-key>
AWS_STORAGE_BUCKET_NAME=skillstream-media
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
```

### 2. Production Settings Architecture

**Production Settings Structure**
```python
# config/settings/production.py
import os
import dj_database_url
from .base import *

# Security Configuration
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static Files Configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files Configuration (AWS S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging Configuration
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
    },
}
```

### 3. CI/CD Pipeline Design

**GitHub Actions Workflow**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements/production.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
        DEBUG: True
      run: |
        python manage.py test
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "skillstream-portfolio"
        heroku_email: ${{secrets.HEROKU_EMAIL}}
        
    - name: Run database migrations
      run: |
        heroku run python manage.py migrate --app skillstream-portfolio
```

### 4. Database Migration Strategy

**Production Database Setup**
```python
# Migration strategy for production
class ProductionDatabaseMigration:
    def setup_heroku_postgres(self):
        """Configure Heroku PostgreSQL addon"""
        # Heroku automatically provides DATABASE_URL
        # Configure connection pooling and performance settings
        
    def migrate_data_from_sqlite(self):
        """Migrate existing data to PostgreSQL"""
        # Export data from SQLite
        # Import data to PostgreSQL
        # Verify data integrity
        
    def setup_database_backups(self):
        """Configure automated backups"""
        # Heroku Postgres automatic backups
        # Custom backup scripts for additional safety
```

### 5. Static and Media File Handling

**WhiteNoise Configuration for Static Files**
```python
# Static files served by WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**AWS S3 Configuration for Media Files**
```python
# Media files stored on AWS S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
```

### 6. Performance Optimization

**Caching Strategy**
```python
# Redis caching for performance
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Cache configuration
CACHE_TTL = 60 * 15  # 15 minutes

# Template caching
@cache_page(CACHE_TTL)
def cached_view(request):
    # Cached view logic
    pass
```

**Database Optimization**
```python
# Database connection pooling
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,  # Connection pooling
        conn_health_checks=True,  # Health checks
    )
}

# Query optimization
class OptimizedVideoQuerySet(models.QuerySet):
    def with_creator_and_stats(self):
        return self.select_related('creator').annotate(
            like_count=Count('likes'),
            comment_count=Count('comment_set')
        )
```

## Security Implementation

### 1. HTTPS and SSL Configuration

**Heroku SSL Setup**
- Automatic SSL certificate management
- Force HTTPS redirects
- HSTS headers for security
- Secure cookie configuration

### 2. Environment Variable Security

**Sensitive Data Management**
```bash
# Never commit these to git
SECRET_KEY=<generated-50-char-secret>
DATABASE_URL=<heroku-postgres-url>
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
EMAIL_HOST_PASSWORD=<email-password>
```

### 3. Security Headers Configuration

**Django Security Settings**
```python
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

## Monitoring and Logging

### 1. Application Monitoring

**Heroku Metrics Integration**
- Application performance monitoring
- Database performance tracking
- Error rate monitoring
- Response time tracking

**Sentry Error Tracking**
```python
# Sentry configuration
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

### 2. Logging Configuration

**Production Logging**
```python
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
```

## Deployment Process

### 1. Pre-deployment Checklist

**Code Preparation**
- [ ] All tests passing
- [ ] Code linted and formatted
- [ ] Security settings configured
- [ ] Environment variables documented
- [ ] Database migrations ready

**Infrastructure Preparation**
- [ ] Heroku app created
- [ ] PostgreSQL addon added
- [ ] Redis addon added (optional)
- [ ] AWS S3 bucket configured
- [ ] Domain name configured (optional)

### 2. Deployment Steps

**Initial Deployment**
1. Create Heroku application
2. Configure environment variables
3. Add PostgreSQL and Redis addons
4. Deploy code via GitHub integration
5. Run database migrations
6. Collect static files
7. Test application functionality

**Continuous Deployment**
1. Push code to main branch
2. GitHub Actions runs tests
3. Automatic deployment to Heroku
4. Database migrations run automatically
5. Application health checks
6. Monitoring and alerting active

### 3. Post-deployment Verification

**Functionality Testing**
- [ ] User registration and login
- [ ] Video upload and viewing
- [ ] Dashboard functionality
- [ ] Social features (likes, comments, subscriptions)
- [ ] Search functionality
- [ ] Mobile responsiveness

**Performance Testing**
- [ ] Page load times
- [ ] Database query performance
- [ ] Media file delivery
- [ ] Concurrent user handling

## Rollback and Recovery

### 1. Rollback Strategy

**Heroku Rollback**
```bash
# Rollback to previous release
heroku rollback --app skillstream-portfolio

# Rollback to specific release
heroku rollback v123 --app skillstream-portfolio
```

### 2. Database Backup and Recovery

**Automated Backups**
- Heroku Postgres automatic daily backups
- Manual backup before major deployments
- Point-in-time recovery capability

**Recovery Process**
```bash
# Create manual backup
heroku pg:backups:capture --app skillstream-portfolio

# Restore from backup
heroku pg:backups:restore b001 DATABASE_URL --app skillstream-portfolio
```

This design provides a comprehensive, production-ready deployment strategy that demonstrates professional-level DevOps skills and modern deployment practices suitable for a portfolio project.