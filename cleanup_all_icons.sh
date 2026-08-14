#!/bin/bash

echo "==============================================="
echo "  CLEANING UP SVG ICONS & RESTORING FONT AWESOME"
echo "==============================================="
echo ""

# 1. Remove all SVG icon usage from templates
echo "1. Removing SVG icons from templates..."
find templates -name "*.html" ! -name "*backup*" -type f -exec sed -i '/<svg.*icon-svg/d' {} \;
find templates -name "*.html" ! -name "*backup*" -type f -exec sed -i '/<svg.*use href/d' {} \;
find templates -name "*.html" ! -name "*backup*" -type f -exec sed -i '/<\/svg>/d' {} \;
find templates -name "*.html" ! -name "*backup*" -type f -exec sed -i '/icon-svg/d' {} \;
echo "   ✅ SVG icons removed"

# 2. Remove SVG styles from base.html
echo "2. Removing SVG styles from base.html..."
sed -i '/icon-svg/d' templates/base.html
sed -i '/<!-- SVG Icon Styles -->/d' templates/base.html
echo "   ✅ SVG styles removed"

# 3. Remove SVG sprite file
echo "3. Removing SVG sprite file..."
rm -rf static/icons/svg/
echo "   ✅ SVG sprite removed"

# 4. Ensure Font Awesome CDN is in base.html
echo "4. Ensuring Font Awesome CDN..."
if ! grep -q "font-awesome" templates/base.html; then
    sed -i '/<head>/a\    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">' templates/base.html
    echo "   ✅ Font Awesome CDN added"
else
    echo "   ✅ Font Awesome CDN already present"
fi

# 5. Add Font Awesome icons to login.html if missing
echo "5. Checking login.html icons..."
if ! grep -q "fa-user" templates/login.html; then
    echo "   ⚠️  Adding icons to login.html..."
    sed -i 's/<input type="text" name="username"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-user"><\/i><\/span><input type="text" name="username"/g' templates/login.html
    sed -i 's/<input type="password" name="password"/<span class="input-icon"><i class="fas fa-lock"><\/i><\/span><input type="password" name="password"/g' templates/login.html
    sed -i 's/<button type="submit" class="btn-login">/<i class="fas fa-sign-in-alt me-2"><\/i>Sign In/g' templates/login.html
    echo "   ✅ Icons added"
else
    echo "   ✅ login.html already has icons"
fi

# 6. Check register.html for SVG icons and remove them
echo "6. Cleaning register.html..."
if [ -f "templates/register.html" ]; then
    # Remove SVG from register.html
    sed -i '/<svg/d' templates/register.html
    sed -i '/<\/svg>/d' templates/register.html
    sed -i '/icon-svg/d' templates/register.html
    sed -i '/use href/d' templates/register.html
    
    # Ensure Font Awesome icons in register.html
    if ! grep -q "fa-user" templates/register.html; then
        echo "   ⚠️  Adding icons to register.html..."
        sed -i 's/<input type="text" name="username"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-user"><\/i><\/span><input type="text" name="username"/g' templates/register.html
        sed -i 's/<input type="email" name="email"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-envelope"><\/i><\/span><input type="email" name="email"/g' templates/register.html
        sed -i 's/<input type="password" name="password1"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-lock"><\/i><\/span><input type="password" name="password1"/g' templates/register.html
        sed -i 's/<input type="password" name="password2"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-lock"><\/i><\/span><input type="password" name="password2"/g' templates/register.html
    fi
    echo "   ✅ register.html cleaned"
fi

# 7. Check all templates for any remaining SVG
echo "7. Checking for remaining SVG usage..."
SVG_REMAINING=$(grep -r "<svg" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
if [ "$SVG_REMAINING" -eq 0 ]; then
    echo "   ✅ No SVG icons found in templates"
else
    echo "   ⚠️  $SVG_REMAINING SVG tags still found"
    grep -l "<svg" templates/*.html 2>/dev/null | grep -v backup | while read file; do
        echo "     - $file"
    done
fi

# 8. Final count
echo ""
echo "==============================================="
echo "  FINAL SUMMARY"
echo "==============================================="
FA_COUNT=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
SVG_COUNT=$(grep -r "<svg" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)

echo "  Font Awesome icons: $FA_COUNT"
echo "  SVG icons: $SVG_COUNT"
echo "  Font Awesome CDN: $(grep -q "font-awesome" templates/base.html && echo "✅" || echo "❌")"
echo ""
echo "✅ Cleanup complete!"
echo "🚀 Restart server: python manage.py runserver"
