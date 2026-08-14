#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Fix the grade_level dropdown - ensure proper option tags
# Find the grade_level select and fix it
pattern = r'<select name="grade_level".*?</select>'

def fix_grade_dropdown(match):
    dropdown = match.group(0)
    
    # Check if options are properly formatted
    if '{% for grade in grade_levels %}' in dropdown:
        # Make sure options have proper HTML
        if '<option value="' not in dropdown:
            # Fix the options
            dropdown = re.sub(
                r'{% for grade in grade_levels %}(.*?){% endfor %}',
                r'{% for grade in grade_levels %}\n                        <option value="{{ grade.id }}">{{ grade.name }}</option>\n                    {% endfor %}',
                dropdown,
                flags=re.DOTALL
            )
    return dropdown

content = re.sub(pattern, fix_grade_dropdown, content, flags=re.DOTALL)

# Also fix the form dropdown
form_pattern = r'<select name="form".*?</select>'
def fix_form_dropdown(match):
    dropdown = match.group(0)
    if '{% for form' in dropdown:
        # Fix form dropdown
        dropdown = re.sub(
            r'{% for form.*?%}(.*?){% endfor %}',
            r'{% for form_key, form_name in forms %}<option value="{{ form_key }}">{{ form_name }}</option>{% endfor %}',
            dropdown,
            flags=re.DOTALL
        )
    return dropdown

content = re.sub(form_pattern, fix_form_dropdown, content, flags=re.DOTALL)

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Fixed admin_dashboard.html dropdowns")
