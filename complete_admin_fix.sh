#!/bin/bash

echo "========================================"
echo "  COMPLETE ADMIN DASHBOARD FIX"
echo "========================================"

# 1. Fix the _get_form_choices function
echo "1. Fixing _get_form_choices function..."
python3 fix_form_choices.py

# 2. Update the template
echo "2. Updating template..."
sed -i 's/{% for form in forms %}/{% for form_key, form_name in forms %}/g' templates/admin_dashboard.html
sed -i 's/{{ form }}/{{ form_name }}/g' templates/admin_dashboard.html
sed -i 's/<option value="{{ form }}"/<option value="{{ form_key }}"/g' templates/admin_dashboard.html

# 3. Verify the form dropdown in template
echo "3. Verifying template..."
grep -A 5 "name=\"form\"" templates/admin_dashboard.html | head -10

# 4. Restart server
echo "4. Restarting server..."
pkill -f "python manage.py runserver" 2>/dev/null
sleep 2

echo ""
echo "✅ Complete! Start the server:"
echo "   python manage.py runserver 8000"
echo ""
echo "Then go to: http://127.0.0.1:8000/admin-dashboard/"
echo "The Form dropdown should show: Form 1 through Form 10"
