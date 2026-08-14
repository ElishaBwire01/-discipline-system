#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find the context dict in admin_dashboard
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    # Check if grade_levels is already in context
    if 'grade_levels' not in func:
        # Find the context = { line
        context_start = func.find('context = {')
        if context_start != -1:
            # Find where to insert - after the first line of context
            insert_pos = start + context_start + 10
            # Find the end of the first line or next line
            insert_after = content.find('\n', insert_pos) + 1
            
            # Insert grade_levels
            content = content[:insert_after] + '        "grade_levels": GradeLevel.objects.filter(is_active=True).order_by("order"),\n' + content[insert_after:]
            
            with open('core/views.py', 'w') as f:
                f.write(content)
            print("✅ Added grade_levels to admin_dashboard context!")
        else:
            print("❌ Could not find context = { in admin_dashboard")
    else:
        print("✅ grade_levels already in admin_dashboard context")
else:
    print("❌ admin_dashboard function not found")
