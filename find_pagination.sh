#!/bin/bash

echo "========================================"
echo "DJANGO PAGINATION INSPECTOR"
echo "========================================"

echo
echo "1. Views using Paginator"
grep -RIn --include="*.py" \
-e "Paginator" \
-e "paginate_by" \
-e "get_page" \
-e "page_obj" \
-e "page_number" \
-e "PageNotAnInteger" \
-e "EmptyPage" .

echo
echo "========================================"

echo
echo "2. URL routes"
grep -RIn --include="urls.py" \
-e "path(" \
-e "re_path(" .

echo
echo "========================================"

echo
echo "3. Render calls"
grep -RIn --include="*.py" \
-e "render(" \
-e "TemplateResponse" .

echo
echo "========================================"

echo
echo "4. Templates using pagination"
grep -RIn --include="*.html" \
-e "page_obj" \
-e "paginator" \
-e "has_next" \
-e "has_previous" \
-e "next_page_number" \
-e "previous_page_number" \
-e "?page=" \
-e "pagination" .

echo
echo "========================================"

echo
echo "5. HTMX / AJAX pagination"
grep -RIn --include="*.html" --include="*.js" \
-e "fetch(" \
-e "axios" \
-e "hx-get" \
-e "hx-post" \
-e "XMLHttpRequest" \
-e "?page=" .

echo
echo "========================================"

echo
echo "6. Models involved"
grep -RIn --include="models.py" \
-e "class " .

echo
echo "========================================"

echo
echo "Finished."
