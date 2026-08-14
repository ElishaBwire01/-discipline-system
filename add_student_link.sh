#!/bin/bash

# Check if the add-student link exists in admin_dashboard
if ! grep -q "add-student" templates/admin_dashboard.html; then
    echo "Adding Add Student link to admin_dashboard..."
    
    # Find the Add Student section and add the link
    sed -i '/Add Student/a\
        <a href="{% url "core:add_student" %}" class="btn btn-primary">\
            <i class="fas fa-plus-circle me-2"></i>Add Student\
        </a>' templates/admin_dashboard.html
    
    echo "✅ Link added to admin_dashboard"
else
    echo "✅ Add Student link already exists"
fi
