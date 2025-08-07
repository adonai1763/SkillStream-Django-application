#!/bin/bash

# Exit on any error
set -e

# Debug: Print environment variables
echo "=== Environment Configuration ==="
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-'Not set'}"
echo "DEBUG: ${DEBUG:-'Not set'}"
echo "PORT: ${PORT:-8000}"
echo "DATABASE_URL: ${DATABASE_URL:+'Set'}"
echo "=================================="

# Validate required environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable is required"
    exit 1
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Start the application
echo "Starting application..."
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120