#!/bin/bash

echo "==============================================="
echo "   REMOVE ALL REMAINING FONT AWESOME ICONS"
echo "==============================================="
echo ""

# Backup all templates first
echo "Creating backup..."
mkdir -p templates/backup_before_fa_removal
cp templates/*.html templates/backup_before_fa_removal/ 2>/dev/null

# Function to replace FA icons in a file
replace_in_file() {
    local file=$1
    echo "Processing: $file"
    
    # Replace common patterns - these are the most common remaining
    sed -i 's|<i class="fas fa-circle" style="color: #10b981; font-size: 8px;"></i>|<svg class="icon-svg icon-circle icon-success" style="width:8px;height:8px;"><use href="/static/icons/svg/icons.svg#icon-circle"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-user fa-4x" style="color: white;"></i>|<svg class="icon-svg icon-user" style="width:4em;height:4em;color:white;"><use href="/static/icons/svg/icons.svg#icon-user"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-key" style="color: #2563eb;"></i>|<svg class="icon-svg icon-key" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-key"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-sync-alt fa-fw" id="refreshIcon" style="cursor: pointer;" onclick="refreshData()"></i>|<svg class="icon-svg icon-sync" id="refreshIcon" style="cursor:pointer;width:1em;height:1em;" onclick="refreshData()"><use href="/static/icons/svg/icons.svg#icon-sync"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-bolt me-1"></i> Live|<svg class="icon-svg icon-bolt" style="width:1em;height:1em;"><use href="/static/icons/svg/icons.svg#icon-bolt"/></svg><span class="icon-label"> Live</span>|g' "$file"
    
    sed -i 's|<i class="fas fa-book"></i>|<svg class="icon-svg icon-book"><use href="/static/icons/svg/icons.svg#icon-book"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-check-circle text-success" style="font-size: 2rem;"></i>|<svg class="icon-svg icon-check-circle icon-success" style="width:2rem;height:2rem;"><use href="/static/icons/svg/icons.svg#icon-check-circle"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-brain text-purple" style="color: #7c3aed;"></i>|<svg class="icon-svg icon-brain" style="color:#7c3aed;"><use href="/static/icons/svg/icons.svg#icon-brain"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-people-group me-1" style="color: #2563eb;"></i>|<svg class="icon-svg icon-users" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-users"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-graduation-cap me-1" style="color: #2563eb;"></i>|<svg class="icon-svg icon-school" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-school"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-info-circle" style="color: #2563eb; font-size: 1.125rem; margin-top: 0.125rem;"></i>|<svg class="icon-svg icon-info-circle" style="color:#2563eb;width:1.125rem;height:1.125rem;"><use href="/static/icons/svg/icons.svg#icon-info-circle"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-chalkboard"></i>|<svg class="icon-svg icon-chalkboard"><use href="/static/icons/svg/icons.svg#icon-chalkboard"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-eye" id="passwordIcon"></i>|<svg class="icon-svg icon-eye" id="passwordIcon"><use href="/static/icons/svg/icons.svg#icon-eye"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-eye" id="password2Icon"></i>|<svg class="icon-svg icon-eye" id="password2Icon"><use href="/static/icons/svg/icons.svg#icon-eye"/></svg>|g' "$file"
    
    sed -i "s|icon.className = 'fas fa-eye-slash';|icon.innerHTML = '<svg class=\"icon-svg icon-eye-slash\"><use href=\"/static/icons/svg/icons.svg#icon-eye-slash\"/></svg>';|g" "$file"
    
    sed -i "s|icon.className = 'fas fa-eye';|icon.innerHTML = '<svg class=\"icon-svg icon-eye\"><use href=\"/static/icons/svg/icons.svg#icon-eye\"/></svg>';|g" "$file"
    
    sed -i "s|matchIndicator.querySelector('.match-icon').className = 'fas fa-check-circle match-icon';|matchIndicator.querySelector('.match-icon').innerHTML = '<svg class=\"icon-svg icon-check-circle icon-success match-icon\"><use href=\"/static/icons/svg/icons.svg#icon-check-circle\"/></svg>';|g" "$file"
    
    sed -i "s|matchIndicator.querySelector('.match-icon').className = 'fas fa-times-circle match-icon';|matchIndicator.querySelector('.match-icon').innerHTML = '<svg class=\"icon-svg icon-close icon-danger match-icon\"><use href=\"/static/icons/svg/icons.svg#icon-close\"/></svg>';|g" "$file"
    
    sed -i "s|matchIndicator.querySelector('.match-icon').className = 'fas fa-info-circle match-icon';|matchIndicator.querySelector('.match-icon').innerHTML = '<svg class=\"icon-svg icon-info-circle icon-info match-icon\"><use href=\"/static/icons/svg/icons.svg#icon-info-circle\"/></svg>';|g" "$file"
    
    sed -i 's|<i class="fas fa-hourglass-half"></i>|<svg class="icon-svg icon-hourglass-half"><use href="/static/icons/svg/icons.svg#icon-hourglass-half"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-sticky-note"></i>|<svg class="icon-svg icon-sticky-note"><use href="/static/icons/svg/icons.svg#icon-sticky-note"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-sticky-note" style="color: #2563eb;"></i>|<svg class="icon-svg icon-sticky-note" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-sticky-note"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-file-alt fa-2x" style="color: #2563eb;"></i>|<svg class="icon-svg icon-file-alt" style="color:#2563eb;width:2em;height:2em;"><use href="/static/icons/svg/icons.svg#icon-file-alt"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-file-excel" style="color: #217346;"></i>|<svg class="icon-svg icon-file-excel" style="color:#217346;"><use href="/static/icons/svg/icons.svg#icon-file-excel"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-file-alt" style="color: #2563eb;"></i>|<svg class="icon-svg icon-file-alt" style="color:#2563eb;"><use href="/static/icons/svg/icons.svg#icon-file-alt"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-file-csv" style="color: #f2a83e;"></i>|<svg class="icon-svg icon-file-csv" style="color:#f2a83e;"><use href="/static/icons/svg/icons.svg#icon-file-csv"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-ban"></i>|<svg class="icon-svg icon-ban"><use href="/static/icons/svg/icons.svg#icon-ban"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-signature"></i>|<svg class="icon-svg icon-signature"><use href="/static/icons/svg/icons.svg#icon-signature"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-toggle-on"></i>|<svg class="icon-svg icon-toggle-on"><use href="/static/icons/svg/icons.svg#icon-toggle-on"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-id-badge"></i>|<svg class="icon-svg icon-id-badge"><use href="/static/icons/svg/icons.svg#icon-id-badge"/></svg>|g' "$file"
    
    sed -i 's|<i class="fas fa-external-link-alt" style="font-size: 0.6rem; opacity: 0.5;"></i>|<svg class="icon-svg icon-external-link-alt" style="width:0.6rem;height:0.6rem;opacity:0.5;"><use href="/static/icons/svg/icons.svg#icon-external-link-alt"/></svg>|g' "$file"
    
    # Handle JavaScript cases
    sed -i "s|'fa-arrow-up text-danger'|'icon-arrow-up icon-danger'|g" "$file"
    sed -i "s|'fa-arrow-down text-success'|'icon-arrow-down icon-success'|g" "$file"
    sed -i "s|'fa-minus text-secondary'|'icon-minus icon-secondary'|g" "$file"
    
    sed -i "s|rec.type === 'critical' ? 'fa-exclamation-triangle'|rec.type === 'critical' ? 'icon-exclamation-triangle'|g" "$file"
    sed -i "s|rec.type === 'warning' ? 'fa-exclamation-circle'|rec.type === 'warning' ? 'icon-exclamation-circle'|g" "$file"
    sed -i "s|rec.type === 'pattern' ? 'fa-chart-bar'|rec.type === 'pattern' ? 'icon-chart-bar'|g" "$file"
    sed -i "s|'fa-check-circle'|'icon-check-circle'|g" "$file"
    
    # Handle circle icons with inline styles
    sed -i 's|<i class="fas fa-circle" style="font-size: 8px;"></i>|<svg class="icon-svg icon-circle" style="width:8px;height:8px;"><use href="/static/icons/svg/icons.svg#icon-circle"/></svg>|g' "$file"
    
    # Handle user-tie icon
    sed -i 's|<i class="fas fa-user-tie fa-3x" style="color: white;"></i>|<svg class="icon-svg icon-user-tie" style="width:3em;height:3em;color:white;"><use href="/static/icons/svg/icons.svg#icon-user-tie"/></svg>|g' "$file"
    
    # Handle el.innerHTML cases
    sed -i "s|el.innerHTML = '<i class=\"fas fa-' + (icon || 'check') + '\"></i> ' + message;|el.innerHTML = '<svg class=\"icon-svg icon-' + (icon || 'check') + '\"><use href=\"/static/icons/svg/icons.svg#icon-' + (icon || 'check') + '\"/></svg> ' + message;|g" "$file"
}

# Process each file with remaining icons
for file in templates/*.html; do
    if [ -f "$file" ] && ! echo "$file" | grep -q "backup"; then
        count=$(grep -c "fa-" "$file" 2>/dev/null)
        if [ "$count" -gt 0 ]; then
            replace_in_file "$file"
        fi
    fi
done

echo ""
echo "==============================================="
echo "✅ FINAL CHECK"
echo "==============================================="

REMAINING=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
echo "Remaining Font Awesome icons: $REMAINING"

if [ "$REMAINING" -gt 0 ]; then
    echo ""
    echo "⚠️  Still $REMAINING icons remain. These may be in complex JavaScript strings."
    echo ""
    echo "To see exactly where:"
    echo "  grep -rn 'fa-' templates/ --include='*.html' | grep -v backup"
    echo ""
    echo "You may need to manually replace these in the JavaScript sections."
else
    echo "✅ ALL Font Awesome icons have been replaced!"
fi

echo ""
echo "Emojis remaining: $(grep -rP '[\x{1F300}-\x{1FAFF}]' templates/ --include='*.html' 2>/dev/null | grep -v backup | wc -l)"
echo "SVG icons used: $(grep -r 'icon-svg' templates/ --include='*.html' 2>/dev/null | grep -v backup | wc -l)"
echo ""
echo "🚀 Restart server: python manage.py runserver"

