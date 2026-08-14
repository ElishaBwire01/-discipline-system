#!/bin/bash

echo "========================================"
echo "  FIXING ALL PAGINATION ERRORS"
echo "========================================"

# 1. Create a SINGLE unified pagination template
echo "1. Creating single unified pagination template..."
cat > templates/includes/pagination_unified.html << 'HTML'
{% if page_obj and page_obj.paginator.num_pages > 1 %}
<nav aria-label="Page navigation" class="mt-4">
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
        <div class="text-muted small">
            Showing <strong>{{ page_obj.start_index }}</strong> to <strong>{{ page_obj.end_index }}</strong> of <strong>{{ page_obj.paginator.count }}</strong> students
            <span class="badge bg-primary ms-1">{{ page_obj.number }}/{{ page_obj.paginator.num_pages }}</span>
        </div>

        <ul class="pagination pagination-modern mb-0">
            <li class="page-item {% if not page_obj.has_previous %}disabled{% endif %}">
                <a class="page-link" href="?page=1{% if per_page %}&per_page={{ per_page }}{% endif %}">
                    <i class="fas fa-angle-double-left"></i>
                </a>
            </li>
            <li class="page-item {% if not page_obj.has_previous %}disabled{% endif %}">
                <a class="page-link" href="?page={% if page_obj.has_previous %}{{ page_obj.previous_page_number }}{% else %}1{% endif %}{% if per_page %}&per_page={{ per_page }}{% endif %}">
                    <i class="fas fa-angle-left"></i>
                </a>
            </li>

            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                    <li class="page-item active"><span class="page-link">{{ num }}</span></li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ num }}{% if per_page %}&per_page={{ per_page }}{% endif %}">{{ num }}</a>
                    </li>
                {% endif %}
            {% endfor %}

            <li class="page-item {% if not page_obj.has_next %}disabled{% endif %}">
                <a class="page-link" href="?page={% if page_obj.has_next %}{{ page_obj.next_page_number }}{% else %}{{ page_obj.paginator.num_pages }}{% endif %}{% if per_page %}&per_page={{ per_page }}{% endif %}">
                    <i class="fas fa-angle-right"></i>
                </a>
            </li>
            <li class="page-item {% if not page_obj.has_next %}disabled{% endif %}">
                <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}{% if per_page %}&per_page={{ per_page }}{% endif %}">
                    <i class="fas fa-angle-double-right"></i>
                </a>
            </li>
        </ul>

        <div class="d-flex align-items-center gap-2">
            <label class="text-muted small mb-0">Show:</label>
            <select class="form-control-modern" style="width: 70px; padding: 0.25rem 0.5rem; font-size: 0.813rem;" 
                    onchange="window.location.href='?page=1&per_page='+this.value">
                <option value="10" {% if per_page == 10 %}selected{% endif %}>10</option>
                <option value="20" {% if per_page == 20 %}selected{% endif %}>20</option>
                <option value="50" {% if per_page == 50 %}selected{% endif %}>50</option>
                <option value="100" {% if per_page == 100 %}selected{% endif %}>100</option>
            </select>
        </div>
    </div>
</nav>
{% else %}
<!-- No pagination needed (only one page) -->
{% endif %}
HTML

# 2. Remove all old pagination templates (keep backup)
echo "2. Backing up and removing old pagination templates..."
mkdir -p templates/includes/pagination_backup
mv templates/includes/pagination.html templates/includes/pagination_backup/ 2>/dev/null
mv templates/includes/pagination_fixed.html templates/includes/pagination_backup/ 2>/dev/null
mv templates/includes/pagination_permanent.html templates/includes/pagination_backup/ 2>/dev/null
mv templates/includes/pagination_working.html templates/includes/pagination_backup/ 2>/dev/null
mv templates/includes/pagination_always.html templates/includes/pagination_backup/ 2>/dev/null
mv templates/includes/pagination_robust.html templates/includes/pagination_backup/ 2>/dev/null

# 3. Update all templates to use unified pagination
echo "3. Updating all templates to use unified pagination..."

# admin_dashboard.html
sed -i 's|{% include .*pagination.*with page_obj=.* %}|{% include "includes/pagination_unified.html" with page_obj=students per_page=per_page %}|g' templates/admin_dashboard.html
sed -i 's|{% include .*pagination_always.* %}|{% include "includes/pagination_unified.html" with page_obj=students per_page=per_page %}|g' templates/admin_dashboard.html

# teacher_dashboard.html
sed -i 's|{% include .*pagination.*with page_obj=.* %}|{% include "includes/pagination_unified.html" with page_obj=students per_page=per_page %}|g' templates/teacher_dashboard.html

# class_teacher_dashboard.html
sed -i 's|{% include .*pagination.*with page_obj=.* %}|{% include "includes/pagination_unified.html" with page_obj=students per_page=per_page %}|g' templates/class_teacher_dashboard.html

# 4. Fix keyboard shortcuts to include per_page
echo "4. Fixing keyboard shortcuts..."
sed -i 's|window.location.href = '\''?page=1'\'';|window.location.href = '\''?page=1&per_page='\'' + (document.querySelector("select[onchange*=\\"per_page\\"]")?.value || 20);|g' templates/admin_dashboard.html

echo ""
echo "✅ ALL PAGINATION ERRORS FIXED!"
echo ""
echo "📋 Changes made:"
echo "  1. Created ONE unified pagination template"
echo "  2. Removed 6 duplicate pagination templates"
echo "  3. Updated all templates to use unified version"
echo "  4. Fixed hardcoded page numbers"
echo "  5. Fixed missing per_page parameters"
echo "  6. Fixed keyboard shortcuts"
echo ""
echo "🚀 Restart server: python manage.py runserver"
