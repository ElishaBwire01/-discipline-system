#!/bin/bash

echo "==============================================="
echo "  RESTORING ALL ICONS"
echo "==============================================="

# Check if Font Awesome CDN is in base.html
if ! grep -q "font-awesome" templates/base.html; then
    echo "Adding Font Awesome CDN..."
    sed -i '/<head>/a\    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">' templates/base.html
fi

# Key icon patterns to add
ICON_PATTERNS=(
    'fa-user'
    'fa-lock'
    'fa-sign-in-alt'
    'fa-users'
    'fa-plus'
    'fa-edit'
    'fa-trash'
    'fa-search'
    'fa-home'
    'fa-cog'
    'fa-bell'
    'fa-eye'
    'fa-eye-slash'
    'fa-check'
    'fa-times'
)

echo "Checking for icons in templates..."
for pattern in "${ICON_PATTERNS[@]}"; do
    count=$(grep -r "$pattern" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
    if [ "$count" -gt 0 ]; then
        echo "  ✅ $pattern: $count found"
    else
        echo "  ⚠️ $pattern: 0 found"
    fi
done

echo ""
echo "Total Font Awesome icons: $(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)"
