import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the edit_student function and add grades to context
if 'def edit_student' in content:
    # Find where context is returned
    pattern = r'(def edit_student.*?return render\(request, "edit_student\.html", context\))'
    
    # Add grades to context before return
    grades_line = """
    # Get grades for dropdown
    school = School.objects.first()
    grades = GradeLevel.objects.filter(school=school, is_active=True).order_by('order') if school else []
    
    context = {
        'student': student,
        'grades': grades,
        'streams': streams,
        'forms': FORM_CHOICES,
    }
    return render(request, "edit_student.html", context)"""
    
    print("🔧 To fix edit_student view, add 'grades' to the context:")
    print("Look for the line: return render(request, 'edit_student.html', context)")
    print("Add 'grades': grades to the context dictionary")
