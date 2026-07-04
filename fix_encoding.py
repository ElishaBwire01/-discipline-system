#!/usr/bin/env python3
# fix_encoding.py - Run this in your project directory

import os
import re
import shutil

# Path to your views.py
views_path = "core/views.py"
backup_path = "core/views.py.backup"

# Create backup
if os.path.exists(views_path):
    shutil.copy2(views_path, backup_path)
    print(f"✅ Backup created: {backup_path}")

# Read the file
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Escaped quotes in docstring
content = content.replace('\\"\\"\\"Test if media files are accessible\\"\\"\\"', '"""Test if media files are accessible"""')

# Fix 2: Replace emojis with text labels
replacements = {
    '🚨': 'ALERT: ',
    '⚠️': 'WARNING: ',
    '🔔': 'NOTICE: ',
    '📈': 'IMPROVING: ',
    '✅': 'SUCCESS: ',
    '📊': 'INFO: ',
    '🔴': 'CRITICAL: ',
    '–': '-',
    '—': '-',
    '�': '',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Fix 3: Specific title fixes
title_fixes = [
    ("'title': 'CRITICAL - Immediate Action Required'", "'title': 'CRITICAL - Immediate Action Required'"),
    ("'title': 'WARNING - Monitor Closely'", "'title': 'WARNING - Monitor Closely'"),
    ("'title': 'Student Status: Good'", "'title': 'Student Status: Good'"),
    ("'title': 'No Interventions Recorded'", "'title': 'No Interventions Recorded'"),
]

for old, new in title_fixes:
    content = content.replace(old, new)

# Fix 4: Fix f-strings with escaped quotes
content = re.sub(r"'title': f'Pattern Detected: {cat\\[\"category__name\"\\]}'", 
                 "'title': f'Pattern Detected: {cat[\"category__name\"]}'", content)
content = re.sub(r"'title': f'Emerging Pattern: {cat\\[\"category__name\"\\]}'", 
                 "'title': f'Emerging Pattern: {cat[\"category__name\"]}'", content)

# Write the fixed content
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Views.py fixed!")
print("🔄 Clearing Python cache...")
os.system("find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null")
print("✅ Done!")

# Check syntax
print("🔍 Checking syntax...")
result = os.system("python -m py_compile core/views.py")
if result == 0:
    print("✅ Syntax check passed!")
else:
    print("❌ Syntax check failed. Please review the file.")