FROM python:3.9-slim

# Env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Workdir
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . /app/

# Static dirs
RUN mkdir -p /app/staticfiles /app/media

# Make start.sh executable
RUN chmod +x /app/start.sh

# Add non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose Railway port (dynamic)
EXPOSE 8000

# Launch via sh
CMD ["sh", "/app/start.sh"]
