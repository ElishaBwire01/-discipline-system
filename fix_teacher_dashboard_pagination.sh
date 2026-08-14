#!/bin/bash

echo "========================================"
echo "  FIX TEACHER DASHBOARD PAGINATION"
echo "========================================"

# Check if the bug exists
if grep -A 20 "def teacher_dashboard" core/views.py | grep -q '"page_obj": students,'; then
    echo "⚠️ Bug found: 'page_obj': students, (students not defined)"
    
    # Fix it
    sed -i '/def teacher_dashboard/,/return render/ s/"page_obj": students,/"page_obj": students_page,/g' core/views.py
    
    echo "✅ Fixed: Changed 'page_obj': students, to 'page_obj': students_page,"
else
    echo "✅ No bug found - teacher_dashboard pagination is correct"
fi

# Verify the fix
echo ""
echo "📋 Verification:"
grep -A 15 "def teacher_dashboard" core/views.py | grep -A 5 "context = {"

echo ""
echo "✅ Fix complete!"
echo "🚀 Restart server: python manage.py runserver"
