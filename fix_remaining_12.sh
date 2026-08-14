#!/bin/bash

echo "==============================================="
echo "   FIX REMAINING 12 FONT AWESOME ICONS"
echo "==============================================="
echo ""

# Show remaining icons with line numbers
echo "📋 Remaining Font Awesome icons:"
echo "-----------------------------------------------"
grep -rn 'fa-' templates/ --include='*.html' | grep -v backup

echo ""
echo "==============================================="
echo "   APPLYING FINAL FIXES"
echo "==============================================="
echo ""

# Fix the specific remaining cases

# 1. Fix the circle in admin_dashboard.html
sed -i 's|<i class="fas fa-circle" style="color: #10b981; font-size: 8px;"></i>|<svg class="icon-svg icon-circle icon-success" style="width:8px;height:8px;"><use href="/static/icons/svg/icons.svg#icon-circle"/></svg>|g' templates/admin_dashboard.html

# 2. Fix the user in admin_profile.html
sed -i 's|<i class="fas fa-user fa-4x" style="color: white;"></i>|<svg class="icon-svg icon-user" style="width:4em;height:4em;color:white;"><use href="/static/icons/svg/icons.svg#icon-user"/></svg>|g' templates/admin_profile.html

# 3. Fix the key in admin_reset_requests.html
sed -i 's|<i class="fas fa-key" style="color: #2563eb;"></i>|<svg class="icon-svg icon-key" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-key"/></svg>|g' templates/admin_reset_requests.html

# 4-6. Fix AI dashboard remaining
sed -i 's|<i class="fas fa-sync-alt fa-fw" id="refreshIcon" style="cursor: pointer;" onclick="refreshData()"></i>|<svg class="icon-svg icon-sync" id="refreshIcon" style="cursor:pointer;width:1em;height:1em;" onclick="refreshData()"><use href="/static/icons/svg/icons.svg#icon-sync"/></svg>|g' templates/ai_dashboard.html
sed -i 's|<i class="fas fa-bolt me-1"></i> Live|<svg class="icon-svg icon-bolt" style="width:1em;height:1em;"><use href="/static/icons/svg/icons.svg#icon-bolt"/></svg><span class="icon-label"> Live</span>|g' templates/ai_dashboard.html
sed -i 's|<i class="fas fa-book"></i>|<svg class="icon-svg icon-book"><use href="/static/icons/svg/icons.svg#icon-book"/></svg>|g' templates/ai_dashboard.html

# 7-8. Fix base.html
sed -i 's|<i class="fas fa-check-circle text-success" style="font-size: 2rem;"></i>|<svg class="icon-svg icon-check-circle icon-success" style="width:2rem;height:2rem;"><use href="/static/icons/svg/icons.svg#icon-check-circle"/></svg>|g' templates/base.html
sed -i 's|<i class="fas fa-brain text-purple" style="color: #7c3aed;"></i>|<svg class="icon-svg icon-brain" style="color:#7c3aed;"><use href="/static/icons/svg/icons.svg#icon-brain"/></svg>|g' templates/base.html

# 9-11. Fix register.html JavaScript
sed -i "s|icon.className = 'fas fa-eye-slash';|icon.innerHTML = '<svg class=\"icon-svg icon-eye-slash\"><use href=\"/static/icons/svg/icons.svg#icon-eye-slash\"/></svg>';|g" templates/register.html
sed -i "s|icon.className = 'fas fa-eye';|icon.innerHTML = '<svg class=\"icon-svg icon-eye\"><use href=\"/static/icons/svg/icons.svg#icon-eye\"/></svg>';|g" templates/register.html
sed -i "s|matchIndicator.querySelector('.match-icon').className = 'fas fa-check-circle match-icon';|matchIndicator.querySelector('.match-icon').innerHTML = '<svg class=\"icon-svg icon-check-circle icon-success match-icon\"><use href=\"/static/icons/svg/icons.svg#icon-check-circle\"/></svg>';|g" templates/register.html

# 12. Fix student_profile.html
sed -i 's|<i class="fas fa-user-tie fa-3x" style="color: white;"></i>|<svg class="icon-svg icon-user-tie" style="width:3em;height:3em;color:white;"><use href="/static/icons/svg/icons.svg#icon-user-tie"/></svg>|g' templates/student_profile.html

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
