#!/usr/bin/env python3
import re

# Read the views.py file
with open('core/views.py', 'r') as f:
    content = f.read()

# Find the school_setup function and add order auto-assignment
# This is a more complex fix - we'll add the logic in the right place

# Look for where grades are created
pattern = r'(GradeLevel\.objects\.create\s*\([^)]*\))'

def add_order_field(match):
    original = match.group(1)
    # Check if order is already specified
    if 'order=' not in original:
        # Add order field before the closing parenthesis
        modified = re.sub(r'\)$', ', order=GradeLevel.objects.filter(school=school).count() + 1)', original)
        return modified
    return original

# This is a simplified fix - you may need to manually edit the file
print("🔧 To fix grade order, add this logic to the view:")
print("""
In core/views.py, in the school_setup view, when creating a GradeLevel:
    
    # Instead of:
    grade = GradeLevel.objects.create(
        school=school,
        name=grade_name,
        code=grade_code,
        is_active=True
    )
    
    # Use:
    next_order = GradeLevel.objects.filter(school=school).count() + 1
    grade = GradeLevel.objects.create(
        school=school,
        name=grade_name,
        code=grade_code,
        order=next_order,
        is_active=True
    )
""")
