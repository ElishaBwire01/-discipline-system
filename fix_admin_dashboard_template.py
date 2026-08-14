#!/usr/bin/env python3
import re

with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Find all Add Student sections
# We want to keep only the one with grade_levels
# Remove the old hardcoded form

# Pattern for the old form (without grade_levels)
old_form_pattern = r'<div class="card-modern mb-4".*?Add Student.*?<form method="post".*?<div class="row g-3">.*?<div class="col-md-2">.*?<select name="stream".*?</select>.*?</div>.*?<div class="col-md-2">.*?<select name="form".*?</select>.*?</div>.*?</form>'

# Find the new form with grade_levels
new_form_pattern = r'<div class="card-modern mb-4".*?Add Student.*?<form method="post".*?<div class="row g-3">.*?<select name="grade_level".*?</select>'

# Check if we have the new form
if 'grade_levels' in content and 'grade_level' in content:
    print("✅ Found grade_level in template")
    
    # Find all Add Student forms
    import re
    forms = re.findall(r'<div class="card-modern mb-4".*?<form method="post".*?</form>', content, re.DOTALL)
    print(f"Found {len(forms)} forms")
    
    # Keep only forms with grade_level
    for i, form in enumerate(forms):
        if 'grade_level' not in form:
            print(f"Removing form {i+1} (no grade_level)")
            content = content.replace(form, '')
        else:
            print(f"Keeping form {i+1} (has grade_level)")
    
    with open('templates/admin_dashboard.html', 'w') as f:
        f.write(content)
    print("✅ Cleaned up admin_dashboard.html")
else:
    print("⚠️ No grade_level found in template")
