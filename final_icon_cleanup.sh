#!/bin/bash

echo "==============================================="
echo "   FINAL ICON CLEANUP - Remove Remaining"
echo "==============================================="
echo ""

# Function to show which icons remain
show_remaining() {
    echo "📋 Remaining Font Awesome icons by file:"
    echo "-----------------------------------------------"
    for file in templates/*.html; do
        if [ -f "$file" ] && ! echo "$file" | grep -q "backup"; then
            count=$(grep -c "fa-" "$file" 2>/dev/null)
            if [ "$count" -gt 0 ]; then
                echo ""
                echo "📄 $file ($count icons)"
                grep -n "fa-" "$file" 2>/dev/null | head -5 | while read line; do
                    echo "   $line"
                done
                if [ "$count" -gt 5 ]; then
                    echo "   ... and $((count - 5)) more"
                fi
            fi
        fi
    done
}

show_remaining

echo ""
echo "==============================================="
echo "   MANUAL REPLACEMENT GUIDE"
echo "==============================================="
echo ""

# Generate replacement commands for each file
echo "🔧 To fix remaining icons, run these commands:"
echo ""

for file in templates/*.html; do
    if [ -f "$file" ] && ! echo "$file" | grep -q "backup"; then
        count=$(grep -c "fa-" "$file" 2>/dev/null)
        if [ "$count" -gt 0 ]; then
            echo "# Fix $file ($count icons)"
            
            # Extract unique icons from this file
            grep -o 'fa-[a-zA-Z0-9-]*' "$file" 2>/dev/null | sort -u | while read icon; do
                # Generate SVG replacement
                svg_name=$(echo "$icon" | sed 's/fa-//g' | sed 's/-/_/g')
                echo "sed -i 's|<i class=\"[^\"]*$icon[^\"]*\"></i>|<svg class=\"icon-svg icon-$svg_name\"><use href=\"/static/icons/svg/icons.svg#$svg_name\"/></svg>|g' $file"
                echo "sed -i 's|<i class=\"[^\"]*$icon[^\"]*\">\([^<]*\)</i>|<svg class=\"icon-svg icon-$svg_name\"><use href=\"/static/icons/svg/icons.svg#$svg_name\"/></svg><span class=\"icon-label\">\1</span>|g' $file"
            done
            echo ""
        fi
    fi
done

echo ""
echo "==============================================="
echo "   QUICK FIX FOR COMMON REMAINING ICONS"
echo "==============================================="
echo ""

# Quick fix for common remaining icons
echo "Running quick fixes for common icons..."

# Fix specific icons that commonly remain
sed -i 's|<i class="[^"]*fa-check[^"]*"></i>|<svg class="icon-svg icon-check"><use href="/static/icons/svg/icons.svg#icon-check"/></svg>|g' templates/*.html
sed -i 's|<i class="[^"]*fa-check[^"]*">\([^<]*\)</i>|<svg class="icon-svg icon-check"><use href="/static/icons/svg/icons.svg#icon-check"/></svg><span class="icon-label">\1</span>|g' templates/*.html

sed -i 's|<i class="[^"]*fa-chevron-[^"]*"></i>|<svg class="icon-svg icon-chevron"><use href="/static/icons/svg/icons.svg#icon-chevron-down"/></svg>|g' templates/*.html

sed -i 's|<i class="[^"]*fa-times[^"]*"></i>|<svg class="icon-svg icon-close"><use href="/static/icons/svg/icons.svg#icon-close"/></svg>|g' templates/*.html

sed -i 's|<i class="[^"]*fa-plus[^"]*"></i>|<svg class="icon-svg icon-plus"><use href="/static/icons/svg/icons.svg#icon-plus"/></svg>|g' templates/*.html

sed -i 's|<i class="[^"]*fa-minus[^"]*"></i>|<svg class="icon-svg icon-minus"><use href="/static/icons/svg/icons.svg#icon-minus"/></svg>|g' templates/*.html

sed -i 's|<i class="[^"]*fa-search[^"]*"></i>|<svg class="icon-svg icon-search"><use href="/static/icons/svg/icons.svg#icon-search"/></svg>|g' templates/*.html

echo "✅ Quick fixes applied"
echo ""
echo "Remaining check:"
REMAINING=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
echo "Remaining Font Awesome icons: $REMAINING"

if [ "$REMAINING" -gt 0 ]; then
    echo ""
    echo "⚠️  Some icons still remain. You may need to manually replace them."
    echo ""
    echo "To see remaining icons:"
    echo "  grep -r 'fa-' templates/ --include='*.html' | grep -v backup"
    echo ""
    echo "Or open the files in a text editor and replace manually."
else
    echo "✅ All Font Awesome icons have been replaced!"
fi

# Fix remaining emojis in register.html
echo ""
echo "Fixing remaining emojis in register.html..."
sed -i 's/✓/<svg class="icon-svg icon-check icon-success" style="width:1.2em;height:1.2em;display:inline-block;"><use href="\/static\/icons\/svg\/icons.svg#icon-check\/"><\/use><\/svg>/g' templates/register.html
sed -i 's/✗/<svg class="icon-svg icon-close icon-danger" style="width:1.2em;height:1.2em;display:inline-block;"><use href="\/static\/icons\/svg\/icons.svg#icon-close\/"><\/use><\/svg>/g' templates/register.html

echo ""
echo "==============================================="
echo "✅ FINAL CLEANUP COMPLETE"
echo "==============================================="
echo ""
echo "📊 Final summary:"
echo "  - Font Awesome icons remaining: $(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)"
echo "  - Emojis remaining: $(grep -rP '[\x{1F300}-\x{1FAFF}]' templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)"
echo "  - SVG icons used: $(grep -r "icon-svg" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)"
echo ""
echo "🚀 Restart server: python manage.py runserver"
echo ""

