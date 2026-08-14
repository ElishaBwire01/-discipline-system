#!/bin/bash

echo "==============================================="
echo "  RESTORING ICONS TO LOGIN PAGE"
echo "==============================================="

# Check if login.html has any icons
if ! grep -q "fa-" templates/login.html; then
    echo "⚠️ No Font Awesome icons found in login.html"
    echo "📝 Adding icons..."
    
    # Add icons to login form
    sed -i 's/<input type="text" name="username"/<div class="input-wrapper"><span class="input-icon"><i class="fas fa-user"><\/i><\/span><input type="text" name="username"/g' templates/login.html
    sed -i 's/<input type="password" name="password"/<span class="input-icon"><i class="fas fa-lock"><\/i><\/span><input type="password" name="password"/g' templates/login.html
    sed -i 's/<button type="submit"/<i class="fas fa-sign-in-alt"><\/i> <button type="submit"/g' templates/login.html
    
    echo "✅ Icons added to login.html"
fi

# Check base.html for icon styles
if ! grep -q "fa-" templates/base.html; then
    echo "⚠️ No Font Awesome icons in base.html"
fi

echo ""
echo "📊 Current status:"
echo "  Font Awesome icons in login.html: $(grep -c "fa-" templates/login.html 2>/dev/null || echo 0)"
echo "  Font Awesome icons in all templates: $(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)"
