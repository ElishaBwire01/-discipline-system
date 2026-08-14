#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Check if grade_levels is in context
    if 'grade_levels' not in content[content.find('def admin_dashboard'):content.find('return render', content.find('def admin_dashboard'))]:
        print("⚠️ Adding grade_levels to admin_dashboard context...")
        
        # Add grade_levels to context
        pattern = r'(context\s*=\s*\{)'
        replacement = r'\1\n        "grade_levels": GradeLevel.objects.filter(is_active=True).order_by("order"),'
        
        # This is a simplified fix - manual edit may be needed
        print("""
Please manually add to admin_dashboard in core/views.py:

Find the context = { line and add:
    'grade_levels': GradeLevel.objects.filter(is_active=True).order_by('order'),
    
Also ensure the import: from .models import GradeLevel, ...
""")
    else:
        print("✅ grade_levels already in admin_dashboard context")
