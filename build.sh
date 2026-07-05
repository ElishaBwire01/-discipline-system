#!/bin/bash
# build.sh - Build script for Vercel

echo "🔧 Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Verify static files
echo "📁 Static files collected:"
ls -la staticfiles/

echo "✅ Build complete!"