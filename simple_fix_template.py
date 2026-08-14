#!/usr/bin/env python3

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Replace the form dropdown with a simple version that works
new_form_dropdown = '''
                    <select name="form" class="form-control-modern" required>
                        <option value="">-- Select Form --</option>
                        {% for form_item in forms %}
                            <option value="{{ form_item }}">{{ form_item }}</option>
                        {% endfor %}
                    </select>'''

# Find and replace
import re
content = re.sub(r'<select name="form".*?</select>', new_form_dropdown, content, flags=re.DOTALL)

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Simplified form dropdown")
