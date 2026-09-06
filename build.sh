#!/bin/bash

set -e

echo "============================================================"
echo " DISCIPLINE SYSTEM - VERCEL BUILD"
echo "============================================================"

echo ""
echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo ""
echo "Checking Django configuration..."
python manage.py check

echo ""
echo "Applying Django database migrations..."
python manage.py migrate --noinput

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo ""
echo "============================================================"
echo " BUILD COMPLETE"
echo "============================================================"
