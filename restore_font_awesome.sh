#!/bin/bash

echo "==============================================="
echo "   RESTORE FONT AWESOME ICONS"
echo "==============================================="
echo ""

# 1. Remove Bootstrap Icons CDN from base.html
echo "1. Removing Bootstrap Icons CDN..."
sed -i '/bootstrap-icons/d' templates/base.html
echo "   ✅ Removed"

# 2. Add Font Awesome CDN to base.html
echo "2. Adding Font Awesome CDN..."
if ! grep -q "font-awesome" templates/base.html; then
    sed -i '/<head>/a\    <!-- Font Awesome 6 Free -->\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">' templates/base.html
    echo "   ✅ Added Font Awesome CDN"
else
    echo "   ✅ Font Awesome CDN already present"
fi

# 3. Convert Bootstrap Icons back to Font Awesome
echo "3. Converting icons back to Font Awesome..."

find templates -name "*.html" ! -name "*backup*" -type f | while read file; do
    echo "Processing: $file"
    
    # Convert bi icons back to fa
    sed -i 's/bi bi-/fas fa-/g' "$file"
    sed -i 's/bi /fas fa-/g' "$file"
    
    # Convert specific icon names
    sed -i 's/fa-person /fa-user /g' "$file"
    sed -i 's/fa-people /fa-users /g' "$file"
    sed -i 's/fa-person-plus /fa-user-plus /g' "$file"
    sed -i 's/fa-person-dash /fa-user-minus /g' "$file"
    sed -i 's/fa-person-gear /fa-user-cog /g' "$file"
    sed -i 's/fa-pencil-square /fa-user-edit /g' "$file"
    sed -i 's/fa-shield-lock /fa-user-shield /g' "$file"
    sed -i 's/fa-clock-history /fa-history /g' "$file"
    sed -i 's/fa-person-badge /fa-user-tie /g' "$file"
    sed -i 's/fa-mortarboard /fa-graduation-cap /g' "$file"
    sed -i 's/fa-house /fa-home /g' "$file"
    sed -i 's/fa-gear /fa-cog /g' "$file"
    sed -i 's/fa-dash /fa-minus /g' "$file"
    sed -i 's/fa-funnel /fa-filter /g' "$file"
    sed -i 's/fa-chevron-left /fa-angle-left /g' "$file"
    sed -i 's/fa-chevron-right /fa-angle-right /g' "$file"
    sed -i 's/fa-chevron-double-left /fa-angle-double-left /g' "$file"
    sed -i 's/fa-chevron-double-right /fa-angle-double-right /g' "$file"
    sed -i 's/fa-chevron-down /fa-chevron-down /g' "$file"
    sed -i 's/fa-chevron-up /fa-chevron-up /g' "$file"
    sed -i 's/fa-file-text /fa-file-alt /g' "$file"
    sed -i 's/fa-filetype-csv /fa-file-csv /g' "$file"
    sed -i 's/fa-file-earmark-excel /fa-file-excel /g' "$file"
    sed -i 's/fa-filetype-pdf /fa-file-pdf /g' "$file"
    sed -i 's/fa-arrow-repeat /fa-sync /g' "$file"
    sed -i 's/fa-box-arrow-right /fa-sign-out-alt /g' "$file"
    sed -i 's/fa-box-arrow-in-right /fa-sign-in-alt /g' "$file"
    sed -i 's/fa-chalkboard /fa-chalkboard-teacher /g' "$file"
    sed -i 's/fa-id-card /fa-id-badge /g' "$file"
    sed -i 's/fa-telephone /fa-phone /g' "$file"
    sed -i 's/fa-send /fa-paper-plane /g' "$file"
    sed -i 's/fa-hammer /fa-gavel /g' "$file"
    sed -i 's/fa-handshake /fa-handshake /g' "$file"
    sed -i 's/fa-chat-dots /fa-comment-dots /g' "$file"
    sed -i 's/fa-chat /fa-comment /g' "$file"
    sed -i 's/fa-chats /fa-comments /g' "$file"
    sed -i 's/fa-lightbulb /fa-lightbulb /g' "$file"
    sed -i 's/fa-list-task /fa-tasks /g' "$file"
    sed -i 's/fa-speedometer2 /fa-tachometer-alt /g' "$file"
    sed -i 's/fa-box-arrow-up-right /fa-external-link-alt /g' "$file"
    sed -i 's/fa-trash3 /fa-trash-alt /g' "$file"
    sed -i 's/fa-sticky /fa-sticky-note /g' "$file"
    sed -i 's/fa-toggle-on /fa-toggle-on /g' "$file"
    sed -i 's/fa-toggle-off /fa-toggle-off /g' "$file"
    sed -i 's/fa-hand-thumbs-up /fa-thumbs-up /g' "$file"
    sed -i 's/fa-hand-thumbs-down /fa-thumbs-down /g' "$file"
    sed -i 's/fa-award /fa-certificate /g' "$file"
done

echo ""
echo "==============================================="
echo "✅ RESTORE COMPLETE"
echo "==============================================="

FA_COUNT=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
BI_COUNT=$(grep -r "bi " templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)

echo "Font Awesome icons: $FA_COUNT"
echo "Bootstrap Icons: $BI_COUNT"

echo ""
echo "🚀 Restart server: python manage.py runserver"
