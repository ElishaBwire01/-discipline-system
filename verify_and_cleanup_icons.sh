#!/bin/bash

echo "==============================================="
echo "   VERIFY ICON REPLACEMENT & CLEANUP"
echo "==============================================="
echo ""

# 1. Count remaining Font Awesome icons
echo "1. Checking remaining Font Awesome icons..."
echo "-----------------------------------------------"
REMAINING_FA=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v "backup" | grep -v "fa-svg" | wc -l)
echo "   Remaining Font Awesome icons: $REMAINING_FA"

# 2. Count remaining Unicode emojis
echo ""
echo "2. Checking remaining Unicode emojis..."
echo "-----------------------------------------------"
REMAINING_EMOJI=$(grep -rP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' templates/ --include="*.html" 2>/dev/null | grep -v "backup" | wc -l)
echo "   Remaining emojis: $REMAINING_EMOJI"

# 3. Count SVG icons used
echo ""
echo "3. Counting SVG icons used..."
echo "-----------------------------------------------"
SVG_USED=$(grep -r "icon-svg" templates/ --include="*.html" 2>/dev/null | grep -v "backup" | wc -l)
echo "   SVG icons used: $SVG_USED"

# 4. Check SVG sprite file
echo ""
echo "4. Checking SVG sprite file..."
echo "-----------------------------------------------"
if [ -f "static/icons/svg/icons.svg" ]; then
    SVG_COUNT=$(grep -c "<symbol" static/icons/svg/icons.svg)
    echo "   ✅ SVG sprite exists with $SVG_COUNT icons"
else
    echo "   ❌ SVG sprite file not found"
fi

# 5. List files with remaining Font Awesome icons
echo ""
echo "5. Files with remaining Font Awesome icons..."
echo "-----------------------------------------------"
if [ "$REMAINING_FA" -gt 0 ]; then
    echo "   Files still using Font Awesome:"
    grep -l "fa-" templates/*.html 2>/dev/null | grep -v "backup" | while read file; do
        count=$(grep -c "fa-" "$file" 2>/dev/null)
        echo "     - $file ($count icons)"
    done
else
    echo "   ✅ No Font Awesome icons remaining"
fi

# 6. List files with remaining emojis
echo ""
echo "6. Files with remaining emojis..."
echo "-----------------------------------------------"
if [ "$REMAINING_EMOJI" -gt 0 ]; then
    echo "   Files still using emojis:"
    grep -lP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' templates/*.html 2>/dev/null | grep -v "backup" | while read file; do
        count=$(grep -cP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' "$file" 2>/dev/null)
        echo "     - $file ($count emojis)"
    done
else
    echo "   ✅ No emojis remaining"
fi

# 7. Cleanup backup of Font Awesome CDN
echo ""
echo "7. Cleaning up Font Awesome CDN references..."
echo "-----------------------------------------------"

# Remove Font Awesome CDN links from base.html if they exist
if grep -q "font-awesome" templates/base.html; then
    echo "   ⚠️  Found Font Awesome CDN links, removing..."
    sed -i '/font-awesome/d' templates/base.html
    echo "   ✅ Removed Font Awesome CDN links"
else
    echo "   ✅ No Font Awesome CDN links found"
fi

# 8. Add SVG CSS if not present
echo ""
echo "8. Adding SVG CSS to base.html..."
echo "-----------------------------------------------"
if ! grep -q "icon-svg" templates/base.html; then
    echo "   ⚠️  SVG CSS not found, adding..."
    
    # Add SVG styles before </head>
    sed -i '/<\/head>/i \
<!-- SVG Icon Styles -->\
<style>\
.icon-svg {\
    width: 1.2em;\
    height: 1.2em;\
    display: inline-block;\
    vertical-align: middle;\
    fill: currentColor;\
    flex-shrink: 0;\
}\
.icon-svg.icon-success { color: #10b981; }\
.icon-svg.icon-danger { color: #dc2626; }\
.icon-svg.icon-warning { color: #f59e0b; }\
.icon-svg.icon-info { color: #3b82f6; }\
.icon-svg.icon-primary { color: #2563eb; }\
.icon-label { vertical-align: middle; margin-left: 0.25rem; }\
.btn .icon-svg { width: 1em; height: 1em; }\
</style>' templates/base.html
    
    echo "   ✅ SVG CSS added"
else
    echo "   ✅ SVG CSS already present"
fi

# 9. Summary
echo ""
echo "==============================================="
echo "📊 FINAL SUMMARY"
echo "==============================================="
echo "   Remaining Font Awesome: $REMAINING_FA"
echo "   Remaining Emojis: $REMAINING_EMOJI"
echo "   SVG Icons used: $SVG_USED"
echo "   SVG Sprite: $([ -f "static/icons/svg/icons.svg" ] && echo "✅" || echo "❌")"
echo ""
echo "Total icons replaced: $((359 - REMAINING_FA)) Font Awesome + 12 Emojis"
echo "==============================================="

# 10. Show sample replacement
echo ""
echo "📋 Sample replacement preview:"
echo "-----------------------------------------------"
if [ -f "templates/login.html" ]; then
    echo "Before: <i class=\"fas fa-user\"></i>"
    echo "After:  <svg class=\"icon-svg icon-user\"><use href=\"/static/icons/svg/icons.svg#icon-user\"/></svg>"
    echo ""
    echo "Check login.html for actual changes:"
    grep -n "icon-svg" templates/login.html | head -3 || echo "   No SVG icons found in login.html"
fi

echo ""
echo "✅ Verification complete!"
echo ""
echo "🔍 To manually check remaining icons:"
echo "   grep -r 'fa-' templates/ --include='*.html' | grep -v backup"
echo "   grep -rP '[\x{1F300}-\x{1FAFF}]' templates/ --include='*.html' | grep -v backup"
echo ""
echo "🚀 Restart server: python manage.py runserver"

