"""
Settings package for SkillStream project.

This package contains environment-specific settings:
- base.py: Common settings shared across all environments
- development.py: Development-specific settings
- production.py: Production-specific settings  
- testing.py: Test-specific settings

Usage:
    Set DJANGO_SETTINGS_MODULE to:
    - config.settings.development (default)
    - config.settings.production
    - config.settings.testing
"""