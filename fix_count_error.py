#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find the line with total_students = students.count()
    # We need to ensure total_students is calculated from students_list, not students
    
    # Look for the pattern
    pattern = r'total_students\s*=\s*students\.count\(\)'
    
    # Check if it exists
    if re.search(pattern, content):
        print("⚠️ Found incorrect count - fixing...")
        
        # Replace with correct count from students_list
        new_content = re.sub(
            pattern,
            'total_students = students_list.count()',  # Use students_list not students
            content
        )
        
        with open('core/views.py', 'w') as f:
            f.write(new_content)
        print("✅ Fixed count issue!")
    else:
        print("✅ Count issue not found or already fixed")
else:
    print("❌ admin_dashboard function not found")
