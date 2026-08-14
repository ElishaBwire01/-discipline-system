#!/bin/bash

echo "========================================"
echo "  FULL PAGINATION AUDIT"
echo "========================================"
echo ""

echo "1. Checking all templates that use pagination:"
echo "----------------------------------------"
grep -r "pagination" templates/ --include="*.html" | grep -v "backup" | grep -v "template_backup"

echo ""
echo "2. Checking pagination includes:"
echo "----------------------------------------"
grep -r "include.*pagination" templates/ --include="*.html" | grep -v "backup"

echo ""
echo "3. Checking page_obj usage in templates:"
echo "----------------------------------------"
grep -r "page_obj" templates/ --include="*.html" | grep -v "backup"

echo ""
echo "4. Checking paginator in views:"
echo "----------------------------------------"
grep -rn "Paginator\|paginator\|page_obj" core/views.py | grep -v "backup" | head -30

echo ""
echo "5. Checking context variables in admin_dashboard:"
echo "----------------------------------------"
grep -A 5 "context = {" core/views.py | grep -A 5 "def admin_dashboard"

echo ""
echo "6. Checking for hardcoded page numbers:"
echo "----------------------------------------"
grep -rn "page=2\|page=1" templates/ --include="*.html" | grep -v "backup"

echo ""
echo "7. Checking per_page handling:"
echo "----------------------------------------"
grep -rn "per_page" core/views.py templates/ --include="*.html" | grep -v "backup" | head -20

echo ""
echo "8. Checking if students is passed to template:"
echo "----------------------------------------"
grep -A 10 "def admin_dashboard" core/views.py | grep "students"

echo ""
echo "9. Checking pagination template files:"
echo "----------------------------------------"
ls -la templates/includes/pagination*.html 2>/dev/null

echo ""
echo "10. Checking for duplicate pagination logic:"
echo "----------------------------------------"
grep -rn "if page_obj.has" templates/ --include="*.html" | grep -v "backup"
