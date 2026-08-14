#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Add debug info before pagination
debug_html = '''
<!-- DEBUG: pagination check -->
{% if page_obj %}
    <div class="alert alert-info">Debug: page_obj exists, has_other_pages: {{ page_obj.has_other_pages }}</div>
{% else %}
    <div class="alert alert-danger">Debug: page_obj is None</div>
{% endif %}
'''

# Insert debug after the table
content = content.replace('</div>\n        {% include', debug_html + '\n        {% include')

with open('templates/admin_dashboard.html', 'w') as f:
    f.write(content)

print("✅ Added debug info to template")
