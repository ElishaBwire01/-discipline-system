#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

if 'def admin_dashboard' in content:
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    if "'page_obj'" not in func and '"page_obj"' not in func:
        print("⚠️ Adding page_obj to context...")
        
        # Find context = {
        context_pos = func.find('context = {')
        if context_pos != -1:
            brace_pos = content.find('{', start + context_pos) + 1
            insert_after = content.find('\n', brace_pos) + 1
            
            new_content = content[:insert_after] + '        "page_obj": students,  # For pagination\n' + content[insert_after:]
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added page_obj to context")
        else:
            print("❌ Could not find context")
    else:
        print("✅ page_obj already in context")
else:
    print("❌ admin_dashboard not found")
