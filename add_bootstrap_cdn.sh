#!/bin/bash

echo "==============================================="
echo "   ADD BOOTSTRAP ICONS CDN"
echo "==============================================="
echo ""

# Check if base.html exists
if [ ! -f "templates/base.html" ]; then
    echo "❌ templates/base.html not found!"
    exit 1
fi

# Check if Bootstrap Icons CDN is already present
if grep -q "bootstrap-icons" templates/base.html; then
    echo "✅ Bootstrap Icons CDN already present"
else
    echo "📝 Adding Bootstrap Icons CDN to base.html..."
    
    # Add Bootstrap Icons CDN after the title or in the head section
    sed -i '/<head>/a\    <!-- Bootstrap Icons -->\n    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">' templates/base.html
    
    echo "✅ Bootstrap Icons CDN added"
fi

# Verify it was added
echo ""
echo "🔍 Verifying Bootstrap Icons CDN in base.html:"
grep -n "bootstrap-icons" templates/base.html || echo "⚠️  Still not found - checking manually..."

echo ""
echo "📊 Current icon status:"
FA_COUNT=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
BI_COUNT=$(grep -r "bi " templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)

echo "  Font Awesome icons: $FA_COUNT (should be 0)"
echo "  Bootstrap Icons used: $BI_COUNT (should be > 0)"

if [ "$FA_COUNT" -eq 0 ] && [ "$BI_COUNT" -gt 0 ]; then
    echo ""
    echo "🎉 All icons successfully converted to Bootstrap Icons!"
else
    echo ""
    echo "⚠️  Some icons may still need attention"
fi

echo ""
echo "🚀 Restart server: python manage.py runserver"
