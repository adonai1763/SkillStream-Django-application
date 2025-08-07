# SkillStream Deployment Guide

This guide provides instructions for deploying SkillStream to various free hosting platforms.

## Project Overview

- **Framework**: Django 5.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **File Storage**: Local filesystem (57MB of media files)
- **Static Files**: Handled by WhiteNoise
- **Size**: ~59MB total project size

## Free Hosting Platform Recommendations

### 1. Railway (Recommended) ⭐
- **Free Tier**: 500 hours/month, 1GB RAM, 1GB storage
- **Database**: Free PostgreSQL included
- **Deployment**: Git-based, automatic deployments
- **Custom Domain**: Supported
- **File Storage**: Persistent (good for media files)

**Pros**: Easy setup, persistent storage, PostgreSQL included
**Cons**: Limited monthly hours

### 2. Render
- **Free Tier**: 750 hours/month, 512MB RAM, limited storage
- **Database**: Free PostgreSQL (90 days, then paid)
- **Deployment**: Git-based, automatic deployments
- **Custom Domain**: Supported
- **File Storage**: Ephemeral (files reset on deploy)

**Pros**: More monthly hours, reliable
**Cons**: Ephemeral storage (not ideal for user uploads)

### 3. Heroku
- **Free Tier**: Discontinued (now paid only)
- **Not recommended** for free deployment

## Deployment Instructions

### Railway Deployment (Recommended)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

3. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Django and use the Dockerfile

4. **Set Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here-generate-new-one
   DJANGO_SETTINGS_MODULE=config.settings.production
   DEBUG=False
   ```

5. **Add PostgreSQL Database**
   - In your project dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set DATABASE_URL

6. **Deploy**
   - Railway will automatically build and deploy
   - Your app will be available at: `https://your-app-name.up.railway.app`

### Render Deployment

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings**
   ```
   Build Command: pip install -r requirements/production.txt
   Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```

4. **Set Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   DJANGO_SETTINGS_MODULE=config.settings.production
   DEBUG=False
   PYTHON_VERSION=3.9.18
   ```

5. **Add PostgreSQL Database** (Optional - 90 days free)
   - Create new PostgreSQL database
   - Copy DATABASE_URL to web service environment variables

## Environment Variables Required

```bash
# Required for all platforms
SECRET_KEY=your-secret-key-here-minimum-50-characters
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False

# Optional - Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Optional - Custom domain
ALLOWED_HOST=yourdomain.com
```

## Generate Secret Key

```python
# Run this in Python to generate a secure secret key
import secrets
print(secrets.token_urlsafe(50))
```

## Pre-deployment Checklist

- [x] Removed unnecessary files (logs, cache, virtual env)
- [x] Optimized media files (reduced from 92MB to 57MB)
- [x] Production settings configured
- [x] Static files handled by WhiteNoise
- [x] Database configuration supports both SQLite and PostgreSQL
- [x] Security settings enabled
- [x] Dockerfile optimized for production

## File Storage Considerations

**Important**: This project includes user-uploaded videos (57MB). Consider:

1. **Railway**: Persistent storage - files survive deployments ✅
2. **Render**: Ephemeral storage - files deleted on each deployment ❌

For production with user uploads, consider:
- Using cloud storage (AWS S3, Cloudinary)
- Railway for persistent local storage
- Implementing file upload limits

## Database Migration

After deployment, run migrations:

```bash
# This happens automatically via start.sh script
python manage.py migrate
```

## Monitoring and Logs

- **Railway**: Built-in logs and metrics dashboard
- **Render**: Built-in logs and monitoring

## Troubleshooting

### Common Issues:

1. **Static files not loading**
   - Ensure `python manage.py collectstatic` runs during build
   - Check STATIC_ROOT and STATICFILES_STORAGE settings

2. **Database connection errors**
   - Verify DATABASE_URL environment variable
   - Check PostgreSQL service is running

3. **Media files not persisting**
   - Use Railway for persistent storage
   - Consider cloud storage for production

4. **Build failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements/production.txt

## Cost Considerations

- **Railway**: Free tier sufficient for small projects
- **Render**: Free tier good for testing, paid for production
- **Database**: PostgreSQL free on Railway, limited free on Render

## Recommended Platform: Railway

Railway is recommended because:
- Persistent file storage (important for video uploads)
- Free PostgreSQL included
- Simple deployment process
- Good free tier limits
- Reliable infrastructure

Deploy to Railway for the best free hosting experience with this video platform.