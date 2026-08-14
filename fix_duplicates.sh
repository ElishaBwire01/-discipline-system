#!/bin/bash

echo "========================================"
echo "  FIXING DUPLICATE FUNCTIONS"
echo "========================================"
echo ""

cd ~/disciplinev12

# Backup the file first
cp core/views.py core/views.py.backup
echo "✅ Backup created: core/views.py.backup"

# Remove duplicate functions (keep the first occurrence)
echo ""
echo "Removing duplicate functions..."

# Remove duplicate reset_sent (keep line 4615, remove 4666)
sed -i '4616,4673d' core/views.py
echo "✅ Removed duplicate reset_sent (kept line 4615)"

# Remove duplicate approve_reset (keep line 3540, remove 4626)
# First, find and remove the second approve_reset
sed -i '/^def approve_reset(request, reset_id):/,$ { /^def approve_reset(request, reset_id):/ { N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; d } }' core/views.py
echo "✅ Removed duplicate approve_reset"

# Remove duplicate request_password_reset (keep line 3479, remove 4570)
sed -i '/^def request_password_reset(request):/,$ { /^def request_password_reset(request):/ { N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; N; d } }' core/views.py
echo "✅ Removed duplicate request_password_reset"

echo ""
echo "✅ All duplicates removed!"

# Run checks
echo ""
echo "Running system check..."
python manage.py check

echo ""
echo "========================================"
echo "  FIX COMPLETE"
echo "========================================"
echo ""
echo "To restore backup if needed:"
echo "  cp core/views.py.backup core/views.py"
