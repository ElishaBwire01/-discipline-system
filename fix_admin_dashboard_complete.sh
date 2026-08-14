#!/bin/bash

echo "========================================"
echo "  FIX ADMIN DASHBOARD GRADE DROPDOWN"
echo "========================================"

# 1. Add grade_levels to view context
echo "1. Adding grade_levels to admin_dashboard view..."
python3 add_grade_levels_to_admin.py

# 2. Update the template
echo "2. Updating admin_dashboard template..."

# Check if grade_level dropdown exists
if grep -q "grade_level" templates/admin_dashboard.html; then
    echo "   ✅ grade_level dropdown already exists"
else
    echo "   📝 Adding grade_level dropdown..."
    # Add grade_level dropdown before the form dropdown
    sed -i '/<select name="form"/i\
                <div class="col-md-2">\
                    <select name="grade_level" class="form-control-modern">\
                        <option value="">-- Select Grade --</option>\
                        {% for grade in grade_levels %}\
                        <option value="{{ grade.id }}">{{ grade.name }}</option>\
                        {% endfor %}\
                    </select>\
                </div>' templates/admin_dashboard.html
    echo "   ✅ Added grade_level dropdown"
fi

# 3. Restart the server
echo "3. Restarting server..."
pkill -f "python manage.py runserver" 2>/dev/null
sleep 2

echo ""
echo "✅ Complete! Start the server:"
echo "   python manage.py runserver 8000"
echo ""
echo "Then go to: http://127.0.0.1:8000/admin-dashboard/"
echo "The Add Student section should now show Grade Level dropdown with Form 1-8 and Grade 10"
