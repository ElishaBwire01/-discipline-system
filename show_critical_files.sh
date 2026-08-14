#!/bin/bash

echo "========================================"
echo "  CRITICAL FILES (SUMMARY VERSION)"
echo "========================================"
echo ""

show_file() {
    echo "📁 $1"
    echo "📝 $2"
    echo "────────────────────────────────────"
    head -50 "$1" 2>/dev/null || echo "⚠️ File not found"
    echo "... (showing first 50 lines)"
    echo "────────────────────────────────────"
    echo ""
}

show_file "core/models.py" "Database models"
show_file "core/forms.py" "Django forms"
show_file "core/views.py" "View functions"
show_file "core/urls.py" "URL routing"
show_file "templates/admin_dashboard.html" "Admin dashboard"
show_file "templates/add_student.html" "Add student page"
show_file ".env" "Environment variables"

echo "✅ Done!"
