#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Find the form dropdown section and fix it
pattern = r'<select name="form".*?</select>'
def fix_form_dropdown(match):
    dropdown = match.group(0)
    
    # Replace the for loop
    dropdown = re.sub(
        r'{% for form_key, form_name in forms %}',
        '{% for form in forms %}',
        dropdown
    )
    
    # Replace the option value
    dropdown = re.sub(
        r'{{ form_key }}',
        '{{ form.id|default:form }}',
        dropdown
    )
    dropdown = re.sub(
        r'{{ form_name }}',
        '{{ form.name|default:form }}',
        dropdown
    )
    
    return dropdown

content = re.sub(pattern, fix_form_dropdown, content, flags=re.DOTALL)

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Fixed form dropdown in admin_dashboard.html")
