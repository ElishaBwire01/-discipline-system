#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the add_student function
start = content.find('def add_student')
if start == -1:
    print("❌ add_student function not found")
    exit()

# Find the end of the function (next 'def' or end of file)
end = content.find('\ndef ', start + 10)
if end == -1:
    end = len(content)

old_func = content[start:end]

# Create new function
new_func = '''def add_student(request):
    """Add a new student to the system."""
    # Check permissions
    if not request.user.is_superuser and not request.user.groups.filter(name__in=['Admin', 'Teacher']).exists():
        messages.error(request, "You don't have permission to add students.")
        return redirect('core:dashboard')

    # Get data for dropdowns
    school = School.objects.first()
    streams = Stream.objects.filter(school=school, is_active=True).order_by('name') if school else Stream.objects.filter(is_active=True).order_by('name')
    grade_levels = GradeLevel.objects.filter(is_active=True).order_by('order')
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

    # GET request - render the form with all dropdown data
    return render(request, 'add_student.html', {
        'streams': streams,
        'grade_levels': grade_levels,
        'forms': forms,
    })
'''

# Replace the function
content = content.replace(old_func, new_func)

with open('core/views.py', 'w') as f:
    f.write(content)

print("✅ add_student view fixed!")
