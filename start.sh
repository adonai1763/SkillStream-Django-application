#!/bin/bash
set -e

echo "=== SKILLSTREAM STARTUP ==="
echo "PORT: $PORT"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting gunicorn on port $PORT..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug