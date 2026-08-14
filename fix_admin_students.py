#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Check if students are in context
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    if "'students'" not in func and '"students"' not in func:
        print("⚠️ 'students' not in admin_dashboard context!")
        print("\n📝 Please add to the context in core/views.py:")
        print("""
    # Get students
    students = Student.objects.filter(is_active=True).select_related('stream', 'grade_level')
    total_students = students.count()
    
    context = {
        'students': students,  # Add this
        'total_students': total_students,
        # ... other context items ...
    }
        """)
    else:
        print("✅ 'students' already in context")
