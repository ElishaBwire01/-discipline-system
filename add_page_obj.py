#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Check if page_obj is already in context
    if "'page_obj'" not in content[content.find('def admin_dashboard'):content.find('return render', content.find('def admin_dashboard'))]:
        print("⚠️ page_obj missing from context - adding...")
        
        # Find the context = { line
        context_pos = content.find('context = {')
        if context_pos != -1:
            # Find the position to insert
            brace_pos = content.find('{', context_pos) + 1
            insert_after = content.find('\n', brace_pos) + 1
            
            # Insert page_obj in context
            new_content = content[:insert_after] + '        "page_obj": students,  # For pagination template\n' + content[insert_after:]
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added page_obj to context!")
        else:
            print("❌ Could not find context = {")
    else:
        print("✅ page_obj already in context")
else:
    print("❌ admin_dashboard function not found")
