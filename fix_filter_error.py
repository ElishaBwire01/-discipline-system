#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    # Find where students.filter is used
    # We need to change students.filter to students_list.filter
    
    # Pattern for critical_count
    pattern1 = r'critical_count = students\.filter\(risk_level="CRITICAL"\)\.count\(\)'
    pattern2 = r'warning_count = students\.filter\(risk_level="WARNING"\)\.count\(\)'
    pattern3 = r'good_count = students\.filter\(risk_level="GOOD"\)\.count\(\)'
    
    # Replace with students_list.filter
    content = re.sub(pattern1, 'critical_count = students_list.filter(risk_level="CRITICAL").count()', content)
    content = re.sub(pattern2, 'warning_count = students_list.filter(risk_level="WARNING").count()', content)
    content = re.sub(pattern3, 'good_count = students_list.filter(risk_level="GOOD").count()', content)
    
    with open('core/views.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed filter errors - using students_list for statistics")
else:
    print("❌ admin_dashboard function not found")
