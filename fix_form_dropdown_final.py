#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Find the form dropdown and replace it
pattern = r'(<select name="form".*?)(<option value="">-- Select Form --</option>.*?)(</select>)'

def replace_form_dropdown(match):
    prefix = match.group(1)
    middle = match.group(2)
    suffix = match.group(3)
    
    # Replace the for loop with a flexible one
    new_middle = '''<option value="">-- Select Form --</option>
                        {% for form_item in forms %}
                            {% if form_item.0 %}
                                <option value="{{ form_item.0 }}">{{ form_item.1 }}</option>
                            {% else %}
                                <option value="{{ form_item.id }}">{{ form_item.name }}</option>
                            {% endif %}
                        {% endfor %}'''
    
    return prefix + new_middle + suffix

# Find the form select tag
form_select_pattern = r'<select name="form".*?</select>'
content = re.sub(form_select_pattern, replace_form_dropdown, content, flags=re.DOTALL)

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Fixed form dropdown to handle both tuples and objects")
