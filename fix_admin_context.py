#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find all context = { blocks in the function
    start = content.find('def admin_dashboard')
    end = content.find('def ', start + 10)
    func = content[start:end]
    
    # Find all context blocks
    context_blocks = []
    pos = 0
    while True:
        ctx_pos = func.find('context = {', pos)
        if ctx_pos == -1:
            break
        # Find matching closing brace
        brace_count = 0
        for i in range(ctx_pos + 11, len(func)):
            if func[i] == '{':
                brace_count += 1
            elif func[i] == '}':
                if brace_count == 0:
                    end_pos = i + 1
                    break
                brace_count -= 1
        context_blocks.append((ctx_pos + start, end_pos + start))
        pos = ctx_pos + 1
    
    print(f"Found {len(context_blocks)} context blocks in admin_dashboard")
    
    # Check the last context block (likely the one used for rendering)
    if context_blocks:
        last_block_start, last_block_end = context_blocks[-1]
        block_content = content[last_block_start:last_block_end]
        
        if 'grade_levels' not in block_content:
            # Add grade_levels to this context
            # Find the opening brace
            brace_pos = block_content.find('{') + 1
            insert_pos = last_block_start + brace_pos + 1
            
            # Insert grade_levels
            new_content = content[:insert_pos] + '\n        "grade_levels": GradeLevel.objects.filter(is_active=True).order_by("order"),' + content[insert_pos:]
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added grade_levels to the main admin_dashboard context!")
        else:
            print("✅ grade_levels already in context")
