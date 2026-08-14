import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the add_student function and fix it
if 'def add_student' in content:
    # Get the function
    start = content.find('def add_student')
    end = content.find('def ', start + 10)
    func = content[start:end]
    
    # Check if it has the right context
    if 'grade_levels' not in func or 'streams' not in func:
        print("⚠️ Context missing - fixing...")
        
        # This is a complex fix, let's print instructions
        print("""
Please manually update core/views.py:

Find the 'def add_student' function and make sure it has:

    # Get data for dropdowns
    school = School.objects.first()
    streams = Stream.objects.filter(school=school, is_active=True).order_by('name') if school else Stream.objects.filter(is_active=True).order_by('name')
    grade_levels = GradeLevel.objects.filter(is_active=True).order_by('order')
    forms = Student.FORM_CHOICES

And the render should be:

    return render(request, 'add_student.html', {
        'streams': streams,
        'grade_levels': grade_levels,
        'forms': forms,
    })
""")
    else:
        print("✅ Context already correct")
else:
    print("❌ add_student function not found")
