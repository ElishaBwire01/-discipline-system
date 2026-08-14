#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the edit_student function context
pattern = r'(def edit_student.*?context\s*=\s*\{)([^}]*)(\})'

def add_grade_levels(match):
    prefix = match.group(1)
    middle = match.group(2)
    suffix = match.group(3)
    
    # Check if grade_levels is already there
    if 'grade_levels' in middle:
        return match.group(0)
    
    # Add grade_levels before the closing brace
    new_middle = middle.rstrip() + ',\n        \'grade_levels\': grade_levels'
    
    # Also add the grade_levels definition before the context
    # This is more complex - we need to find where to add the import
    return prefix + new_middle + suffix

# This is a simplified fix - let's just print instructions
print("🔧 To fix edit_student view, manually add 'grade_levels' to context:")
print("""
1. Open core/views.py
2. Find 'def edit_student'
3. Find 'context = {'
4. Add these lines BEFORE the context:

    # Get grade levels for dropdown
    school = School.objects.first()
    grade_levels = GradeLevel.objects.filter(school=school, is_active=True).order_by('order') if school else []

5. Add to context:
        'grade_levels': grade_levels,

6. Make sure to import GradeLevel at the top of views.py if not already there:
    from .models import GradeLevel, School
""")

# Check if GradeLevel is imported
if 'from .models import' in content and 'GradeLevel' not in content:
    print("\n⚠️ GradeLevel needs to be imported at the top of views.py")
    print("Add 'GradeLevel' to the models import line")
elif 'GradeLevel' not in content:
    print("\n⚠️ GradeLevel is not imported in views.py")
    print("Add: from .models import School, GradeLevel, Student, ...")

