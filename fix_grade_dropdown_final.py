#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Fix grade_level dropdown
grade_pattern = r'(<select name="grade_level".*?)(<option value="">-- Select Grade --</option>.*?)(</select>)'

def replace_grade_dropdown(match):
    prefix = match.group(1)
    middle = match.group(2)
    suffix = match.group(3)
    
    # Ensure proper option tags
    new_middle = '''<option value="">-- Select Grade --</option>
                        {% for grade in grade_levels %}
                            <option value="{{ grade.id }}">{{ grade.name }}</option>
                        {% endfor %}'''
    
    return prefix + new_middle + suffix

content = re.sub(grade_pattern, replace_grade_dropdown, content, flags=re.DOTALL)

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Fixed grade_level dropdown")
