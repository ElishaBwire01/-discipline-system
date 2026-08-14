#!/bin/bash

echo "==============================================="
echo "   CHECK ACTUAL ICON STATUS"
echo "==============================================="
echo ""

echo "1. Checking Font Awesome icons..."
FA_COUNT=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
echo "   Font Awesome icons: $FA_COUNT"

echo ""
echo "2. Checking Bootstrap Icons..."
BI_COUNT=$(grep -r "bi " templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
echo "   Bootstrap Icons: $BI_COUNT"

echo ""
echo "3. Checking what's actually in the files..."
echo "-----------------------------------------------"
grep -rn "class=\".*bi" templates/ --include="*.html" 2>/dev/null | grep -v backup | head -10

echo ""
echo "4. Checking for Font Awesome in files..."
echo "-----------------------------------------------"
grep -rn "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | head -10

echo ""
echo "5. Checking base.html for icon CDN..."
echo "-----------------------------------------------"
grep -n "bootstrap-icons\|font-awesome" templates/base.html

echo ""
echo "6. Checking a sample file..."
echo "-----------------------------------------------"
echo "First 5 icon classes in login.html:"
grep -o 'class="[^"]*"' templates/login.html 2>/dev/null | grep -E "fa-|bi" | head -5

echo ""
echo "==============================================="
echo "   APPLYING FIXES"
echo "==============================================="
echo ""

# Check if Bootstrap Icons CDN is in base.html
if ! grep -q "bootstrap-icons" templates/base.html; then
    echo "Adding Bootstrap Icons CDN to base.html..."
    sed -i '/<link rel="stylesheet"/a\    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">' templates/base.html
    echo "✅ Added"
fi

# Actually replace the icons in the files
echo ""
echo "Replacing icons in all template files..."

# Loop through all html files and replace fa- with bi bi-
find templates -name "*.html" ! -name "*backup*" -type f | while read file; do
    echo "Processing: $file"
    
    # Replace fa- classes with bi classes
    sed -i 's/class="[^"]*fa-[a-zA-Z0-9-]*[^"]*"/class="bi bi-icon"/g' "$file"
    
    # More specific: replace the pattern
    sed -i 's/<i class="fas /<i class="bi /g' "$file"
    sed -i 's/<i class="far /<i class="bi /g' "$file"
    sed -i 's/<i class="fal /<i class="bi /g' "$file"
    sed -i 's/<i class="fab /<i class="bi /g' "$file"
    sed -i 's/<i class="fa /<i class="bi /g' "$file"
    
    # Replace specific icons with Bootstrap equivalents
    sed -i 's/fa-user /bi-person /g' "$file"
    sed -i 's/fa-users /bi-people /g' "$file"
    sed -i 's/fa-lock /bi-lock /g' "$file"
    sed -i 's/fa-key /bi-key /g' "$file"
    sed -i 's/fa-school /bi-building /g' "$file"
    sed -i 's/fa-plus /bi-plus /g' "$file"
    sed -i 's/fa-minus /bi-dash /g' "$file"
    sed -i 's/fa-edit /bi-pencil /g' "$file"
    sed -i 's/fa-trash /bi-trash /g' "$file"
    sed -i 's/fa-search /bi-search /g' "$file"
    sed -i 's/fa-download /bi-download /g' "$file"
    sed -i 's/fa-upload /bi-upload /g' "$file"
    sed -i 's/fa-filter /bi-funnel /g' "$file"
    sed -i 's/fa-flag /bi-flag /g' "$file"
    sed -i 's/fa-bell /bi-bell /g' "$file"
    sed -i 's/fa-clock /bi-clock /g' "$file"
    sed -i 's/fa-calendar /bi-calendar /g' "$file"
    sed -i 's/fa-home /bi-house /g' "$file"
    sed -i 's/fa-cog /bi-gear /g' "$file"
    sed -i 's/fa-eye /bi-eye /g' "$file"
    sed -i 's/fa-eye-slash /bi-eye-slash /g' "$file"
    sed -i 's/fa-check /bi-check /g' "$file"
    sed -i 's/fa-check-circle /bi-check-circle /g' "$file"
    sed -i 's/fa-times /bi-x /g' "$file"
    sed -i 's/fa-times-circle /bi-x-circle /g' "$file"
    sed -i 's/fa-info-circle /bi-info-circle /g' "$file"
    sed -i 's/fa-exclamation /bi-exclamation /g' "$file"
    sed -i 's/fa-exclamation-circle /bi-exclamation-circle /g' "$file"
    sed -i 's/fa-exclamation-triangle /bi-exclamation-triangle /g' "$file"
    sed -i 's/fa-robot /bi-robot /g' "$file"
    sed -i 's/fa-brain /bi-cpu /g' "$file"
    sed -i 's/fa-chart-bar /bi-bar-chart /g' "$file"
    sed -i 's/fa-chart-line /bi-graph-up /g' "$file"
    sed -i 's/fa-chart-pie /bi-pie-chart /g' "$file"
    sed -i 's/fa-arrow-left /bi-arrow-left /g' "$file"
    sed -i 's/fa-arrow-right /bi-arrow-right /g' "$file"
    sed -i 's/fa-arrow-up /bi-arrow-up /g' "$file"
    sed -i 's/fa-arrow-down /bi-arrow-down /g' "$file"
    sed -i 's/fa-angle-left /bi-chevron-left /g' "$file"
    sed -i 's/fa-angle-right /bi-chevron-right /g' "$file"
    sed -i 's/fa-chevron-down /bi-chevron-down /g' "$file"
    sed -i 's/fa-chevron-up /bi-chevron-up /g' "$file"
    sed -i 's/fa-file /bi-file /g' "$file"
    sed -i 's/fa-file-alt /bi-file-text /g' "$file"
    sed -i 's/fa-file-csv /bi-filetype-csv /g' "$file"
    sed -i 's/fa-file-excel /bi-file-earmark-excel /g' "$file"
    sed -i 's/fa-file-pdf /bi-filetype-pdf /g' "$file"
    sed -i 's/fa-sync /bi-arrow-repeat /g' "$file"
    sed -i 's/fa-sync-alt /bi-arrow-repeat /g' "$file"
    sed -i 's/fa-spinner /bi-arrow-repeat /g' "$file"
    sed -i 's/fa-sign-out-alt /bi-box-arrow-right /g' "$file"
    sed -i 's/fa-sign-in-alt /bi-box-arrow-in-right /g' "$file"
    sed -i 's/fa-graduation-cap /bi-mortarboard /g' "$file"
    sed -i 's/fa-user-graduate /bi-mortarboard /g' "$file"
    sed -i 's/fa-chalkboard-teacher /bi-chalkboard /g' "$file"
    sed -i 's/fa-people-group /bi-people /g' "$file"
    sed -i 's/fa-id-badge /bi-id-card /g' "$file"
    sed -i 's/fa-crown /bi-crown /g' "$file"
    sed -i 's/fa-phone /bi-telephone /g' "$file"
    sed -i 's/fa-envelope /bi-envelope /g' "$file"
    sed -i 's/fa-camera /bi-camera /g' "$file"
    sed -i 's/fa-save /bi-save /g' "$file"
    sed -i 's/fa-paper-plane /bi-send /g' "$file"
    sed -i 's/fa-gavel /bi-hammer /g' "$file"
    sed -i 's/fa-shield-alt /bi-shield /g' "$file"
    sed -i 's/fa-handshake /bi-handshake /g' "$file"
    sed -i 's/fa-comment-dots /bi-chat-dots /g' "$file"
    sed -i 's/fa-comment /bi-chat /g' "$file"
    sed -i 's/fa-comments /bi-chats /g' "$file"
    sed -i 's/fa-circle /bi-circle /g' "$file"
    sed -i 's/fa-book /bi-book /g' "$file"
    sed -i 's/fa-bookmark /bi-bookmark /g' "$file"
    sed -i 's/fa-briefcase /bi-briefcase /g' "$file"
    sed -i 's/fa-bullhorn /bi-megaphone /g' "$file"
    sed -i 's/fa-calculator /bi-calculator /g' "$file"
    sed -i 's/fa-clipboard /bi-clipboard /g' "$file"
    sed -i 's/fa-copy /bi-copy /g' "$file"
    sed -i 's/fa-link /bi-link /g' "$file"
    sed -i 's/fa-external-link-alt /bi-box-arrow-up-right /g' "$file"
    sed -i 's/fa-history /bi-clock-history /g' "$file"
    sed -i 's/fa-lightbulb /bi-lightbulb /g' "$file"
    sed -i 's/fa-tag /bi-tag /g' "$file"
    sed -i 's/fa-tags /bi-tags /g' "$file"
    sed -i 's/fa-list /bi-list /g' "$file"
    sed -i 's/fa-tasks /bi-list-task /g' "$file"
    sed -i 's/fa-inbox /bi-inbox /g' "$file"
    sed -i 's/fa-dashboard /bi-speedometer2 /g' "$file"
    sed -i 's/fa-tachometer-alt /bi-speedometer2 /g' "$file"
    sed -i 's/fa-user-plus /bi-person-plus /g' "$file"
    sed -i 's/fa-user-minus /bi-person-dash /g' "$file"
    sed -i 's/fa-user-cog /bi-person-gear /g' "$file"
    sed -i 's/fa-user-edit /bi-pencil-square /g' "$file"
    sed -i 's/fa-user-shield /bi-shield-lock /g' "$file"
    sed -i 's/fa-user-clock /bi-clock-history /g' "$file"
    sed -i 's/fa-user-tag /bi-tag /g' "$file"
    sed -i 's/fa-user-tie /bi-person-badge /g' "$file"
    sed -i 's/fa-credit-card /bi-credit-card /g' "$file"
    sed -i 's/fa-print /bi-printer /g' "$file"
    sed -i 's/fa-trash-alt /bi-trash3 /g' "$file"
    sed -i 's/fa-arrow-circle-left /bi-arrow-left-circle /g' "$file"
    sed -i 's/fa-arrow-circle-right /bi-arrow-right-circle /g' "$file"
    sed -i 's/fa-arrow-circle-up /bi-arrow-up-circle /g' "$file"
    sed -i 's/fa-arrow-circle-down /bi-arrow-down-circle /g' "$file"
    sed -i 's/fa-angle-double-left /bi-chevron-double-left /g' "$file"
    sed -i 's/fa-angle-double-right /bi-chevron-double-right /g' "$file"
    sed -i 's/fa-file-export /bi-file-export /g' "$file"
    sed -i 's/fa-file-import /bi-file-import /g' "$file"
    sed -i 's/fa-sticky-note /bi-sticky /g' "$file"
    sed -i 's/fa-ban /bi-ban /g' "$file"
    sed -i 's/fa-toggle-on /bi-toggle-on /g' "$file"
    sed -i 's/fa-toggle-off /bi-toggle-off /g' "$file"
    sed -i 's/fa-globe /bi-globe /g' "$file"
    sed -i 's/fa-university /bi-building /g' "$file"
    sed -i 's/fa-certificate /bi-award /g' "$file"
    sed -i 's/fa-medal /bi-award /g' "$file"
    sed -i 's/fa-trophy /bi-trophy /g' "$file"
    sed -i 's/fa-star /bi-star /g' "$file"
    sed -i 's/fa-star-half /bi-star-half /g' "$file"
    sed -i 's/fa-thumbs-up /bi-hand-thumbs-up /g' "$file"
    sed -i 's/fa-thumbs-down /bi-hand-thumbs-down /g' "$file"
    sed -i 's/fa-hand-peace /bi-hand-peace /g' "$file"
    sed -i 's/fa-handshake /bi-handshake /g' "$file"
    sed -i 's/fa-hand-holding-heart /bi-hand-heart /g' "$file"
    
    # Fix class attribute for Bootstrap Icons
    sed -i 's/class="bi bi-/class="bi /g' "$file"
    sed -i 's/class="bi-"/class="bi /g' "$file"
done

echo ""
echo "==============================================="
echo "✅ FINAL VERIFICATION"
echo "==============================================="

FA_REMAINING=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
BI_TOTAL=$(grep -r "bi " templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)

echo "Font Awesome icons remaining: $FA_REMAINING"
echo "Bootstrap Icons used: $BI_TOTAL"

if [ "$FA_REMAINING" -eq 0 ] && [ "$BI_TOTAL" -gt 0 ]; then
    echo "✅ SUCCESS! All icons converted to Bootstrap Icons!"
elif [ "$FA_REMAINING" -gt 0 ]; then
    echo "⚠️  Still $FA_REMAINING Font Awesome icons remain"
    echo "Listing remaining icons:"
    grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | head -20
else
    echo "⚠️  No Bootstrap Icons found. Something went wrong."
    echo "Check a sample file:"
    grep -o 'class="[^"]*"' templates/login.html | head -10
fi

echo ""
echo "🚀 Restart server: python manage.py runserver"
