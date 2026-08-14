#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find where context is defined
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    # Check if students are already in context
    if "'students'" not in func and '"students"' not in func:
        # Find the context = { line
        context_pos = func.find('context = {')
        if context_pos != -1:
            # Find where to insert (after the opening brace)
            insert_pos = start + context_pos + 11
            # Find the first line break after the brace
            line_break = content.find('\n', insert_pos) + 1
            
            # Insert students at the beginning of context
            new_content = content[:line_break] + '        "students": students,\n        "total_students": total_students,\n' + content[line_break:]
            
            # Also need to define students before context
            # Find where to define students (before context)
            define_pos = content.find('pending_resets =', start)
            if define_pos != -1:
                define_line = content.find('\n', define_pos) + 1
                students_definition = '''    # Get all students for display
    students = Student.objects.filter(is_active=True).select_related('stream', 'grade_level')
    total_students = students.count()
    
'''
                new_content = new_content[:define_line] + students_definition + new_content[define_line:]
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added students to admin_dashboard context!")
        else:
            print("❌ Could not find context = {")
    else:
        print("✅ students already in context")
else:
    print("❌ admin_dashboard function not found")
