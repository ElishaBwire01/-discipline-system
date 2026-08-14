#!/usr/bin/env python3
import re

with open('templates/includes/pagination_fixed.html', 'r') as f:
    content = f.read()

# Add debug info at the top
debug = '''
<!-- PAGINATION DEBUG -->
{% if page_obj %}
    <div class="alert alert-info small">
        Debug: page_obj exists | Number: {{ page_obj.number }} | Total: {{ page_obj.paginator.num_pages }} | per_page: {{ per_page }}
    </div>
{% else %}
    <div class="alert alert-danger small">
        Debug: page_obj is None! per_page: {{ per_page }}
    </div>
{% endif %}
'''

content = content.replace('<nav aria-label="Page navigation"', debug + '<nav aria-label="Page navigation"')

with open('templates/includes/pagination_fixed.html', 'w') as f:
    f.write(content)

print("✅ Added debug info to pagination")
