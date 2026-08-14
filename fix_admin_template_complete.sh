#!/bin/bash

echo "========================================"
echo "  FIX ADMIN DASHBOARD TEMPLATE"
echo "========================================"

# Backup the template
cp templates/admin_dashboard.html templates/admin_dashboard.html.backup_$(date +%s)

# Find the Add Student section and replace it with a clean version
cat > templates/admin_dashboard_new.html << 'HTML'
<!-- Add Student Section -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-plus-circle"></i></span>
        Add Student
        <a href="{% url 'core:add_student' %}" class="btn btn-sm btn-outline-light float-end">
            <i class="fas fa-external-link-alt"></i> Advanced Form
        </a>
    </div>
    <div class="card-body p-4">
        <form method="post" action="{% url 'core:admin_dashboard' %}">
            {% csrf_token %}
            <input type="hidden" name="action" value="add_student">
            <div class="row g-3">
                <div class="col-md-3">
                    <input type="text" name="admission_number" class="form-control-modern" placeholder="Admission Number" required>
                </div>
                <div class="col-md-3">
                    <input type="text" name="name" class="form-control-modern" placeholder="Full Name" required>
                </div>
                <div class="col-md-2">
                    <select name="stream" class="form-control-modern" required>
                        <option value="">-- Select Stream --</option>
                        {% for stream in streams %}
                        <option value="{{ stream.id }}">{{ stream.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <select name="grade_level" class="form-control-modern">
                        <option value="">-- Select Grade --</option>
                        {% for grade in grade_levels %}
                        <option value="{{ grade.id }}">{{ grade.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <select name="form" class="form-control-modern" required>
                        <option value="">-- Select Form --</option>
                        {% for form_key, form_name in forms %}
                        <option value="{{ form_key }}">{{ form_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-12">
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="fas fa-save me-1"></i>Add Student
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>
HTML

# Replace the old Add Student section with the new one
# This is complex - let's do it manually
echo ""
echo "📝 Please manually replace the Add Student section in templates/admin_dashboard.html"
echo "   Find the old 'Add Student' form and replace it with the content from:"
echo "   templates/admin_dashboard_new.html"
echo ""
echo "Or run this command to open the file for editing:"
echo "   nano templates/admin_dashboard.html"
