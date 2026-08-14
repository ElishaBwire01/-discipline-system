#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find the context = { line in admin_dashboard
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    # Check if grade_levels is already in context
    if 'grade_levels' not in func:
        # Find the context = { line
        context_line = func.find('context = {')
        if context_line != -1:
            # Find where context ends (the closing })
            # We'll insert after the first line of context
            context_start = start + context_line
            # Find the position to insert (after the opening brace)
            brace_pos = content.find('{', context_start) + 1
            # Find the next line break after the brace
            insert_pos = content.find('\n', brace_pos) + 1
            
            # Insert grade_levels
            new_content = content[:insert_pos] + '        "grade_levels": GradeLevel.objects.filter(is_active=True).order_by("order"),\n' + content[insert_pos:]
            
            # Also make sure GradeLevel is imported
            if 'from .models import' in new_content and 'GradeLevel' not in new_content:
                # Add GradeLevel to imports
                new_content = new_content.replace('from .models import', 'from .models import GradeLevel, ')
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added grade_levels to admin_dashboard context!")
            print("✅ Also added GradeLevel to imports")
        else:
            print("❌ Could not find context = {")
    else:
        print("✅ grade_levels already in context")
else:
    print("❌ admin_dashboard function not found")
