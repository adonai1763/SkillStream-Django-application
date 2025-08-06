#!/bin/bash

# SkillStream Test Runner Script
# This script runs the complete test suite with coverage reporting

set -e

echo "🧪 Running SkillStream test suite..."

# Activate virtual environment if it exists
if [ -d "skillstream_env" ]; then
    source skillstream_env/bin/activate
fi

# Set test environment
export DJANGO_SETTINGS_MODULE=config.settings.testing

# Run code quality checks
echo "🔍 Running code quality checks..."

echo "  📏 Checking code formatting with black..."
black --check core config || {
    echo "❌ Code formatting issues found. Run 'black core config' to fix."
    exit 1
}

echo "  📦 Checking import sorting with isort..."
isort --check-only core config || {
    echo "❌ Import sorting issues found. Run 'isort core config' to fix."
    exit 1
}

echo "  🔎 Running flake8 linting..."
flake8 core config

echo "✅ Code quality checks passed!"

# Run tests with coverage
echo "🏃 Running tests with coverage..."
coverage run --source='.' manage.py test

# Generate coverage report
echo "📊 Generating coverage report..."
coverage report -m
coverage html

echo ""
echo "✅ All tests passed!"
echo "📈 Coverage report generated in htmlcov/index.html"
echo ""

# Check coverage threshold
coverage_percentage=$(coverage report | tail -1 | awk '{print $4}' | sed 's/%//')
threshold=80

if (( $(echo "$coverage_percentage >= $threshold" | bc -l) )); then
    echo "🎉 Coverage ($coverage_percentage%) meets the threshold ($threshold%)"
else
    echo "⚠️  Coverage ($coverage_percentage%) is below the threshold ($threshold%)"
    echo "   Consider adding more tests to improve coverage"
fi