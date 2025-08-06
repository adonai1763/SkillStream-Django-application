#!/bin/bash

# SkillStream Deployment Script
# This script handles deployment tasks for production

set -e

echo "🚀 SkillStream Deployment Script"

# Check if we're in production mode
if [ "$DJANGO_SETTINGS_MODULE" != "config.settings.production" ]; then
    echo "⚠️  Warning: Not using production settings"
    echo "   Set DJANGO_SETTINGS_MODULE=config.settings.production"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check required environment variables
required_vars=("SECRET_KEY" "ALLOWED_HOSTS" "DB_NAME" "DB_USER" "DB_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements/production.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Check deployment configuration
echo "🔍 Checking deployment configuration..."
python manage.py check --deploy

# Create superuser if it doesn't exist (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📝 Post-deployment checklist:"
echo "  - Update DNS records if needed"
echo "  - Configure SSL certificates"
echo "  - Set up monitoring and logging"
echo "  - Test all critical functionality"
echo "  - Update documentation"