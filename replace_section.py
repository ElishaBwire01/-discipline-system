#!/usr/bin/env python3

# Read the new section
with open('templates/admin_dashboard_new.html', 'r') as f:
    new_section = f.read()

# Read the template
with open('templates/admin_dashboard.html', 'r') as f:
    content = f.read()

# Find the old Add Student section
import re

# Pattern to match the entire Add Student card
pattern = r'<!-- Add Student -->.*?<div class="card-modern mb-4".*?</div>\s*</div>'

# Find all matches
matches = list(re.finditer(pattern, content, re.DOTALL))

if matches:
    # Use the first match (there might be multiple)
    start = matches[0].start()
    end = matches[0].end()
    
    # Replace with new section
    new_content = content[:start] + new_section + content[end:]
    
    # Write back
    with open('templates/admin_dashboard.html', 'w') as f:
        f.write(new_content)
    
    print("✅ Replaced Add Student section successfully!")
    print(f"   Removed {end - start} characters")
    print(f"   Added {len(new_section)} characters")
else:
    print("❌ Could not find the Add Student section")
    print("   The pattern might be different. Looking for alternative...")
    
    # Alternative pattern
    pattern2 = r'<div class="card-modern mb-4".*?Add Student.*?</div>\s*</div>'
    matches2 = list(re.finditer(pattern2, content, re.DOTALL))
    if matches2:
        start = matches2[0].start()
        end = matches2[0].end()
        new_content = content[:start] + new_section + content[end:]
        with open('templates/admin_dashboard.html', 'w') as f:
            f.write(new_content)
        print("✅ Replaced using alternative pattern!")
    else:
        print("❌ Still could not find the section. Manual editing required.")
        print("   Please open templates/admin_dashboard.html and replace the Add Student section manually.")
