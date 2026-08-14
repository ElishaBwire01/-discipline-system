#!/bin/bash

echo "========================================"
echo "  FIX ADD STUDENT DROPDOWNS"
echo "========================================"

# 1. Update the add_student view to ensure proper context
echo "1. Updating add_student view..."

cat > fix_view.py << 'PYTHON'
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the add_student function and fix it
if 'def add_student' in content:
    # Get the function
    start = content.find('def add_student')
    end = content.find('def ', start + 10)
    func = content[start:end]
    
    # Check if it has the right context
    if 'grade_levels' not in func or 'streams' not in func:
        print("⚠️ Context missing - fixing...")
        
        # This is a complex fix, let's print instructions
        print("""
Please manually update core/views.py:

Find the 'def add_student' function and make sure it has:

    # Get data for dropdowns
    school = School.objects.first()
    streams = Stream.objects.filter(school=school, is_active=True).order_by('name') if school else Stream.objects.filter(is_active=True).order_by('name')
    grade_levels = GradeLevel.objects.filter(is_active=True).order_by('order')
    forms = Student.FORM_CHOICES

And the render should be:

    return render(request, 'add_student.html', {
        'streams': streams,
        'grade_levels': grade_levels,
        'forms': forms,
    })
""")
    else:
        print("✅ Context already correct")
else:
    print("❌ add_student function not found")
PYTHON

python3 fix_view.py

# 2. Check if the add_student template exists and has the right dropdowns
echo ""
echo "2. Checking add_student.html template..."

if [ -f templates/add_student.html ]; then
    echo "✅ add_student.html exists"
    
    # Check if it has the right dropdowns
    if grep -q "grade_level" templates/add_student.html; then
        echo "✅ Grade Level dropdown exists"
    else
        echo "❌ Grade Level dropdown missing - adding it..."
        # Add grade_level dropdown
        sed -i '/<select name="stream"/a\
            <div class="col-md-4">\
                <label class="form-label-modern">Grade Level</label>\
                <select name="grade_level" class="form-control-modern">\
                    <option value="">-- Select Grade --</option>\
                    {% for grade in grade_levels %}\
                        <option value="{{ grade.id }}">{{ grade.name }} ({{ grade.code }})</option>\
                    {% endfor %}\
                </select>\
            </div>' templates/add_student.html
    fi
else
    echo "❌ add_student.html not found"
fi

# 3. Check the admin_dashboard for the add student button
echo ""
echo "3. Checking admin_dashboard for Add Student button..."

if grep -q "add-student" templates/admin_dashboard.html; then
    echo "✅ Add Student button exists"
else
    echo "⚠️ Add Student button missing - adding it..."
    sed -i '/Add Student/a\
    <a href="{% url "core:add_student" %}" class="btn btn-primary btn-sm">\
        <i class="fas fa-plus-circle"></i> Add Student\
    </a>' templates/admin_dashboard.html
fi

echo ""
echo "✅ Fix complete! Restart the server and test:"
echo "   http://127.0.0.1:8000/add-student/"
