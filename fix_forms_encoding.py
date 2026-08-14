#!/usr/bin/env python3
import os

# Read the file as bytes
with open('core/forms.py', 'rb') as f:
    content_bytes = f.read()

# Try to decode with error handling
try:
    # Try UTF-8 with replacement
    content = content_bytes.decode('utf-8', errors='replace')
    
    # Replace corrupted characters
    content = content.replace('�', '')
    
    # Write back with UTF-8
    with open('core/forms.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed encoding issues in forms.py")
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Alternative: try Latin-1
    content = content_bytes.decode('latin-1')
    with open('core/forms.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed using Latin-1 fallback")
