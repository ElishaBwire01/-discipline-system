#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function and fix it
if 'def admin_dashboard' in content:
    # Check if students is defined before use
    # Look for the pattern where students is used but not defined
    if 'total_students = students.count()' in content:
        # Find the section and add students definition
        # Look for the start of admin_dashboard
        start = content.find('def admin_dashboard')
        
        # Find where students should be defined (after the function start)
        # Look for the line with total_students
        pos = content.find('total_students = students.count()')
        if pos != -1:
            # Find the indentation level
            line_start = content.rfind('\n', 0, pos) + 1
            indent = content[line_start:pos] - content[line_start:pos].lstrip()
            indent_str = ' ' * (len(indent) if indent else 4)
            
            # Insert students definition before total_students
            insert_pos = pos
            insert_text = f'\n{indent_str}# Get all students\n{indent_str}students = Student.objects.filter(is_active=True).select_related("stream", "grade_level")\n{indent_str}total_students = students.count()\n{indent_str}'
            
            # Remove the old total_students line and replace with new
            # Find the end of the total_students line
            end_pos = content.find('\n', pos)
            content = content[:pos] + insert_text + content[end_pos+1:]
            
            with open('core/views.py', 'w') as f:
                f.write(content)
            print("✅ Fixed admin_dashboard view")
        else:
            print("⚠️ Could not find total_students line")
    else:
        print("✅ admin_dashboard already fixed")
else:
    print("❌ admin_dashboard function not found")
