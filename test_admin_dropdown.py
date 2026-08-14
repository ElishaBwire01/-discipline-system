#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import GradeLevel

User = get_user_model()

# Login
client = Client()
user = User.objects.get(username='Elisha')
client.force_login(user)

# Get admin dashboard
response = client.get('/admin-dashboard/')
content = response.content.decode('utf-8')

print("✅ Checking admin dashboard for grade options...")
print("-" * 50)

# Check for each grade
grades = GradeLevel.objects.filter(is_active=True).order_by('order')
found = []
missing = []

for grade in grades:
    if grade.name in content:
        found.append(grade.name)
    else:
        missing.append(grade.name)

if found:
    print(f"✅ Found in HTML: {', '.join(found)}")
if missing:
    print(f"❌ Missing from HTML: {', '.join(missing)}")

# Check specifically for the dropdown
if 'name="grade_level"' in content:
    print("✅ grade_level dropdown found")
    
    # Extract the dropdown section
    import re
    match = re.search(r'<select name="grade_level".*?</select>', content, re.DOTALL)
    if match:
        dropdown = match.group(0)
        options = re.findall(r'>([^<]+)</option>', dropdown)
        print(f"📊 Options in dropdown: {len(options) - 1}")  # -1 for the "-- Select Grade --" option
        for opt in options[1:]:  # Skip the first option
            print(f"  - {opt}")
else:
    print("❌ grade_level dropdown not found")
