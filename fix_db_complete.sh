#!/bin/bash

echo "========================================"
echo "  COMPLETE DATABASE RESET"
echo "========================================"
echo ""

cd ~/disciplinev12

# Kill any running server
echo "1. Stopping any running servers..."
pkill -9 -f "python" 2>/dev/null
sleep 1

# Backup old database if exists
if [ -f "db.sqlite3" ]; then
    echo "2. Backing up old database..."
    mv db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
fi

# Delete migration files
echo "3. Cleaning migration files..."
find core/migrations/ -name "*.py" ! -name "__init__.py" -delete
find core/migrations/ -name "*.pyc" -delete

# Make fresh migrations
echo "4. Creating fresh migrations..."
python manage.py makemigrations core

# Apply migrations
echo "5. Applying migrations..."
python manage.py migrate

# Create superuser
echo "6. Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "7. Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check system
echo "8. Running system check..."
python manage.py check

echo ""
echo "========================================"
echo "  ✅ DATABASE RESET COMPLETE!"
echo "========================================"
echo ""
echo "Start the server:"
echo "  python manage.py runserver"
echo ""
echo "Or on a different port:"
echo "  python manage.py runserver 8001"
echo ""
echo "Visit: http://127.0.0.1:8000/"
echo "========================================"
