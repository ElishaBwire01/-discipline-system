#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the edit_student function
if 'def edit_student' in content:
    # Check if grade_levels is already in context
    if 'grade_levels' not in content or 'grade_levels' not in content[content.find('def edit_student'):content.find('return render', content.find('def edit_student'))]:
        print("⚠️ grade_levels not found in edit_student context")
        print("\n📝 Please manually add to core/views.py:")
        print("""
In the edit_student function, find the context dictionary and add:
    
    # Get grade levels for dropdown
    from .models import School, GradeLevel
    school = School.objects.first()
    grade_levels = GradeLevel.objects.filter(school=school, is_active=True).order_by('order') if school else []
    
    context = {
        'student': student,
        'grade_levels': grade_levels,  # ADD THIS LINE
        'streams': streams,
        'forms': FORM_CHOICES,
    }
""")
    else:
        print("✅ grade_levels already in context")
else:
    print("❌ edit_student function not found")
