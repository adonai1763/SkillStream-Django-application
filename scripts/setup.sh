#!/bin/bash

# SkillStream Development Setup Script
# This script sets up the development environment for SkillStream

set -e  # Exit on any error

echo "🎬 Setting up SkillStream development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "skillstream_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv skillstream_env
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source skillstream_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements/development.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

echo ""
echo "🎉 Setup complete! To get started:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source skillstream_env/bin/activate"
echo ""
echo "2. Edit the .env file with your configuration"
echo ""
echo "3. Create a superuser (optional):"
echo "   python manage.py createsuperuser"
echo ""
echo "4. Run the development server:"
echo "   python manage.py runserver"
echo ""
echo "5. Visit http://127.0.0.1:8000 to see your application"
echo ""
echo "📖 For more information, see the README.md file"