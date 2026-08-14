#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find and replace the _get_form_choices function
old_function = '''def _get_form_choices():
    """Return grade-level form choices as objects (same pattern as streams)."""
    active_grades = GradeLevel.objects.filter(is_active=True).order_by("order", "name")
    if active_grades.exists():
        return active_grades
    default_choices = []
    for i, name in enumerate(['Form 1', 'Form 2', 'Form 3', 'Form 4'], 1):
        default_choices.append({
            'id': i,
            'name': name,
            'code': f'F{i}',
            'order': i,
            'is_active': True
        })
    return default_choices'''

new_function = '''def _get_form_choices():
    """Return form choices as tuples (key, value) for dropdowns."""
    from .models import Student
    return Student.FORM_CHOICES'''

if old_function in content:
    content = content.replace(old_function, new_function)
    with open('core/views.py', 'w') as f:
        f.write(content)
    print("✅ Fixed _get_form_choices function")
else:
    print("⚠️ Could not find the exact function. Manual edit may be needed.")
