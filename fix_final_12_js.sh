#!/bin/bash

echo "==============================================="
echo "   FIX FINAL 12 JS FONT AWESOME ICONS"
echo "==============================================="
echo ""

# Show remaining icons with line numbers
echo "📋 Final 12 Font Awesome icons to fix:"
echo "-----------------------------------------------"
grep -rn 'fa-' templates/ --include='*.html' | grep -v backup

echo ""
echo "==============================================="
echo "   APPLYING FINAL JS FIXES"
echo "==============================================="
echo ""

# 1. Fix user_profile_settings.html dynamic icon
sed -i "s|el.innerHTML = '<i class=\"fas fa-' + (icon || 'check') + '\"></i> ' + message;|el.innerHTML = '<svg class=\"icon-svg icon-' + (icon || 'check') + '\"><use href=\"/static/icons/svg/icons.svg#icon-' + (icon || 'check') + '\"/></svg> ' + message;|g" templates/user_profile_settings.html

# 2. Fix student_profile.html online/offline badges
sed -i 's|<i class="fas fa-circle me-1" style="font-size: 8px;"></i>|<svg class="icon-svg icon-circle" style="width:8px;height:8px;display:inline-block;"><use href="/static/icons/svg/icons.svg#icon-circle"/></svg>|g' templates/student_profile.html

# 3-7. Fix ai_dashboard.html icon mappings
sed -i "s|'fa-chart-bar'|'icon-chart-bar'|g" templates/ai_dashboard.html
sed -i "s|'fa-calendar-day'|'icon-calendar-day'|g" templates/ai_dashboard.html
sed -i "s|'fa-user-graduate'|'icon-user-graduate'|g" templates/ai_dashboard.html
sed -i "s|'fa-chart-line'|'icon-chart-line'|g" templates/ai_dashboard.html
sed -i "s|'fa-info-circle'|'icon-info-circle'|g" templates/ai_dashboard.html

# 8. Fix ai_dashboard.html table icon
sed -i 's|<i class="fas fa-table me-2"></i>|<svg class="icon-svg icon-table" style="width:1em;height:1em;"><use href="/static/icons/svg/icons.svg#icon-table"/></svg>|g' templates/ai_dashboard.html

# 9-10. Fix ai_dashboard.html spin classes
sed -i "s|icon.classList.add('fa-spin')|icon.classList.add('icon-spin')|g" templates/ai_dashboard.html
sed -i "s|icon.classList.remove('fa-spin')|icon.classList.remove('icon-spin')|g" templates/ai_dashboard.html

# 11-12. Fix toast icon mapping
sed -i "s|info: 'fa-info-circle',|info: 'icon-info-circle',|g" templates/ai_dashboard.html
sed -i "s|warning: 'fa-exclamation-triangle',|warning: 'icon-exclamation-triangle',|g" templates/ai_dashboard.html
sed -i "s|danger: 'fa-exclamation-circle'|danger: 'icon-exclamation-circle'|g" templates/ai_dashboard.html

# Also fix the toast message generation
sed -i "s|toast.className = 'toast align-items-center text-white ' + colors[type] + ' border-0 position-fixed bottom-0 end-0 m-3';|toast.className = 'toast align-items-center text-white ' + colors[type] + ' border-0 position-fixed bottom-0 end-0 m-3';|g" templates/ai_dashboard.html

# Also fix any remaining fa- in the file
sed -i 's|fa-exclamation-triangle|icon-exclamation-triangle|g' templates/ai_dashboard.html
sed -i 's|fa-info-circle|icon-info-circle|g' templates/ai_dashboard.html
sed -i 's|fa-circle|icon-circle|g' templates/ai_dashboard.html

echo ""
echo "==============================================="
echo "✅ FINAL VERIFICATION"
echo "==============================================="

REMAINING=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
echo "Remaining Font Awesome icons: $REMAINING"

if [ "$REMAINING" -eq 0 ]; then
    echo "🎉 ALL Font Awesome icons have been replaced!"
else
    echo "⚠️  Still $REMAINING icons remain:"
    grep -rn 'fa-' templates/ --include='*.html' | grep -v backup
fi

echo ""
echo "📊 Final Statistics:"
echo "  - SVG icons used: $(grep -r 'icon-svg' templates/ --include='*.html' 2>/dev/null | grep -v backup | wc -l)"
echo "  - Emojis remaining: $(grep -rP '[\x{1F300}-\x{1FAFF}]' templates/ --include='*.html' 2>/dev/null | grep -v backup | wc -l)"
echo ""
echo "🚀 Restart server: python manage.py runserver"
