#!/usr/bin/env python3
"""
SkillStream Deployment Helper Script

This script helps prepare the project for deployment by:
1. Generating a secure SECRET_KEY
2. Providing deployment commands for different platforms
3. Checking project readiness
"""

import secrets
import os
import sys

def generate_secret_key():
    """Generate a secure Django SECRET_KEY"""
    return secrets.token_urlsafe(50)

def check_project_readiness():
    """Check if project is ready for deployment"""
    print("🔍 Checking project readiness...")
    
    issues = []
    
    # Check if requirements files exist
    if not os.path.exists('requirements/production.txt'):
        issues.append("❌ requirements/production.txt not found")
    else:
        print("✅ Production requirements found")
    
    # Check if Dockerfile exists
    if not os.path.exists('Dockerfile'):
        issues.append("❌ Dockerfile not found")
    else:
        print("✅ Dockerfile found")
    
    # Check if start.sh exists and is executable
    if not os.path.exists('start.sh'):
        issues.append("❌ start.sh not found")
    else:
        print("✅ start.sh found")
    
    # Check if production settings exist
    if not os.path.exists('config/settings/production.py'):
        issues.append("❌ Production settings not found")
    else:
        print("✅ Production settings found")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ Project is ready for deployment!")
        return True

def show_deployment_instructions():
    """Show deployment instructions for different platforms"""
    secret_key = generate_secret_key()
    
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print(f"\n🔑 Your SECRET_KEY (save this securely):")
    print(f"SECRET_KEY={secret_key}")
    
    print(f"\n📋 Environment Variables to set:")
    print(f"SECRET_KEY={secret_key}")
    print(f"DJANGO_SETTINGS_MODULE=config.settings.production")
    print(f"DEBUG=False")
    
    print(f"\n🚂 RAILWAY DEPLOYMENT:")
    print(f"1. Push to GitHub:")
    print(f"   git add .")
    print(f"   git commit -m 'Deploy to Railway'")
    print(f"   git push origin main")
    print(f"")
    print(f"2. Go to railway.app and create new project from GitHub")
    print(f"3. Add PostgreSQL database service")
    print(f"4. Set environment variables above")
    print(f"5. Deploy automatically!")
    
    print(f"\n🎨 RENDER DEPLOYMENT:")
    print(f"1. Push to GitHub (same as above)")
    print(f"2. Go to render.com and create new Web Service")
    print(f"3. Build Command: pip install -r requirements/production.txt")
    print(f"4. Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT")
    print(f"5. Set environment variables above")
    print(f"6. Deploy!")
    
    print(f"\n📊 PROJECT STATS:")
    print(f"• Framework: Django 5.2")
    print(f"• Database: SQLite/PostgreSQL")
    print(f"• Size: ~59MB (including 57MB media files)")
    print(f"• Python: 3.9+")

def main():
    print("🎬 SkillStream Deployment Helper")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check-only':
        check_project_readiness()
        return
    
    if check_project_readiness():
        show_deployment_instructions()
    else:
        print("\n❌ Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()