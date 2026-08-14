#!/bin/bash

echo "========================================"
echo "  FIXING ADD STUDENT PAGE"
echo "========================================"

# 1. Check if add_student view exists
echo "1. Checking for add_student view..."
if ! grep -q "def add_student" core/views.py; then
    echo "   ❌ add_student view not found - creating it..."
    
    # Add the view to views.py
    cat >> core/views.py << 'VIEW'
@login_required
def add_student(request):
    """Add a new student to the system."""
    # Check permissions
    if not request.user.is_superuser and not request.user.groups.filter(name__in=['Admin', 'Teacher']).exists():
        messages.error(request, "You don't have permission to add students.")
        return redirect('core:dashboard')
    
    # Get data for dropdowns
    school = School.objects.first()
    streams = Stream.objects.filter(school=school, is_active=True).order_by('name') if school else []
    grade_levels = GradeLevel.objects.filter(school=school, is_active=True).order_by('order') if school else []
    forms = Student.FORM_CHOICES
    
    if request.method == 'POST':
        # Create student
        try:
            admission_number = request.POST.get('admission_number', '').strip()
            name = request.POST.get('name', '').strip()
            stream_id = request.POST.get('stream')
            grade_level_id = request.POST.get('grade_level')
            form = request.POST.get('form')
            year = request.POST.get('year', timezone.now().year)
            optional_notes = request.POST.get('optional_notes', '').strip()
            
            # Validate
            if not admission_number or not name:
                messages.error(request, "Admission number and name are required.")
                return render(request, 'add_student.html', {
                    'streams': streams,
                    'grade_levels': grade_levels,
                    'forms': forms,
                })
            
            # Get stream
            stream = Stream.objects.get(id=stream_id) if stream_id else None
            grade_level = GradeLevel.objects.get(id=grade_level_id) if grade_level_id else None
            
            # Create student
            student = Student.objects.create(
                admission_number=admission_number,
                name=name,
                stream=stream,
                grade_level=grade_level,
                form=form,
                year=year,
                optional_notes=optional_notes,
                created_by=request.user
            )
            
            messages.success(request, f"Student '{student.name}' added successfully!")
            return redirect('core:student_profile', student_id=student.id)
            
        except Exception as e:
            messages.error(request, f"Error adding student: {e}")
    
    return render(request, 'add_student.html', {
        'streams': streams,
        'grade_levels': grade_levels,
        'forms': forms,
    })
VIEW
    echo "   ✅ add_student view created"
else
    echo "   ✅ add_student view exists"
fi

# 2. Add URL pattern for add_student
echo "2. Adding URL pattern..."
if ! grep -q "add-student" core/urls.py; then
    # Add URL before the last pattern
    sed -i '/urlpatterns = \[/a\    path("add-student/", views.add_student, name="add_student"),' core/urls.py
    echo "   ✅ URL pattern added"
else
    echo "   ✅ URL pattern already exists"
fi

# 3. Create the add_student template
echo "3. Creating add_student.html template..."
cat > templates/add_student.html << 'HTML'
{% extends 'base.html' %}
{% load static %}

{% block title %}Add Student - {{ school_name|default:"Disciplinary System" }}{% endblock %}

{% block content %}
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-user-plus"></i></span>
        Add Student
        <a href="{% url 'core:bulk_upload_students' %}" class="btn btn-sm btn-outline-light float-end">
            <i class="fas fa-file-upload"></i> Bulk Upload
        </a>
    </div>
    <div class="card-body">
        <form method="post" class="row g-3">
            {% csrf_token %}
            
            <div class="col-md-6">
                <label class="form-label-modern">Admission Number *</label>
                <input type="text" name="admission_number" class="form-control-modern" 
                       placeholder="e.g., 2024-001" required>
            </div>
            
            <div class="col-md-6">
                <label class="form-label-modern">Full Name *</label>
                <input type="text" name="name" class="form-control-modern" 
                       placeholder="Enter full name" required>
            </div>
            
            <div class="col-md-4">
                <label class="form-label-modern">Stream/Class</label>
                <select name="stream" class="form-control-modern">
                    <option value="">-- Select Stream --</option>
                    {% for stream in streams %}
                        <option value="{{ stream.id }}">{{ stream.name }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="col-md-4">
                <label class="form-label-modern">Grade Level</label>
                <select name="grade_level" class="form-control-modern">
                    <option value="">-- Select Grade --</option>
                    {% for grade in grade_levels %}
                        <option value="{{ grade.id }}">{{ grade.name }} ({{ grade.code }})</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="col-md-4">
                <label class="form-label-modern">Form</label>
                <select name="form" class="form-control-modern">
                    <option value="">-- Select Form --</option>
                    {% for form_key, form_name in forms %}
                        <option value="{{ form_key }}">{{ form_name }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="col-md-12">
                <label class="form-label-modern">Year</label>
                <input type="number" name="year" class="form-control-modern" 
                       value="{% now 'Y' %}" required>
            </div>
            
            <div class="col-12">
                <label class="form-label-modern">Optional Notes</label>
                <textarea name="optional_notes" class="form-control-modern" rows="3" 
                          placeholder="Any additional information about the student..."></textarea>
            </div>
            
            <div class="col-12">
                <button type="submit" class="btn-modern btn-modern-primary">
                    <i class="fas fa-save me-2"></i>Add Student
                </button>
                <a href="{% url 'core:dashboard' %}" class="btn-modern btn-modern-secondary">
                    <i class="fas fa-times me-2"></i>Cancel
                </a>
            </div>
        </form>
    </div>
</div>

<style>
    .form-label-modern {
        font-weight: 600;
        font-size: 0.875rem;
        color: #334155;
        margin-bottom: 0.375rem;
        display: block;
    }
    .form-control-modern {
        width: 100%;
        padding: 0.625rem 0.875rem;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        font-size: 0.9375rem;
        transition: all 0.3s;
        background: #f8fafc;
    }
    .form-control-modern:focus {
        border-color: #2563eb;
        background: white;
        outline: none;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
    }
</style>
{% endblock %}
HTML
echo "   ✅ add_student.html template created"

echo ""
echo "✅ Complete! Now you can access: http://127.0.0.1:8000/add-student/"
echo "   The dropdowns will show data from the database."
