#!/bin/sh

# Exit on error
set -e

# Use Railway-provided PORT or fallback
if [ -z "$PORT" ]; then
    PORT=8000
fi

# Debug
echo "=== ENV ==="
echo "PORT: $PORT"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-'Not set'}"
echo "DEBUG: ${DEBUG:-'Not set'}"
echo "SECRET_KEY: ${SECRET_KEY:+Set}"
echo "======================"

# Required
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is missing"
    exit 1
fi

# Migrations & Static
echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Migrating DB..."
python manage.py migrate

# Launch app
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
