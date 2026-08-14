#!/bin/bash

# Check if grade_level dropdown exists
if grep -q "grade_level" templates/edit_student.html; then
    echo "✅ grade_level dropdown already exists in template"
else
    echo "📝 Adding grade_level dropdown to template..."
    
    # Add grade_level dropdown before the form dropdown
    sed -i '/name="form"/i\
                            <div class="col-md-6">\
                                <label class="form-label-modern">Grade Level</label>\
                                <select name="grade_level" class="form-control-modern" required>\
                                    <option value="">Select grade level...</option>\
                                    {% for grade in grade_levels %}\
                                        <option value="{{ grade.id }}" {% if student.grade_level.id == grade.id %}selected{% endif %}>{{ grade.name }} ({{ grade.code }})</option>\
                                    {% endfor %}\
                                </select>\
                            </div>' templates/edit_student.html
    
    echo "✅ Added grade_level dropdown"
fi
