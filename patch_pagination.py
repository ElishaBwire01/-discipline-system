#!/usr/bin/env python3
import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Find the admin_dashboard function
if 'def admin_dashboard' in content:
    start = content.find('def admin_dashboard')
    end = content.find('return render', start)
    func = content[start:end]
    
    # Check if pagination is already there
    if 'Paginator' not in func:
        print("✅ Adding pagination to admin_dashboard...")
        
        # Find where students are defined
        students_line = func.find('students = Student.objects.filter')
        if students_line != -1:
            # Replace the students definition with paginated version
            old_students = func[students_line:func.find('\n', students_line)]
            
            # Find where to insert pagination code
            insert_pos = start + students_line
            line_end = content.find('\n', insert_pos) + 1
            
            # Create new pagination code
            pagination_code = '''    # Get all students for display with pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    students_list = Student.objects.filter(is_active=True).select_related('stream', 'grade_level')
    total_students = students_list.count()
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    paginator = Paginator(students_list, per_page)
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
'''
            
            # Replace the old students line with pagination code
            new_content = content[:insert_pos] + pagination_code + content[line_end:]
            
            # Also add per_page to context
            context_pos = new_content.find('context = {')
            if context_pos != -1:
                # Find the opening brace
                brace_pos = new_content.find('{', context_pos) + 1
                insert_after = new_content.find('\n', brace_pos) + 1
                new_content = new_content[:insert_after] + '        "per_page": per_page,  # For pagination\n' + new_content[insert_after:]
            
            with open('core/views.py', 'w') as f:
                f.write(new_content)
            print("✅ Added pagination to admin_dashboard!")
        else:
            print("❌ Could not find students definition")
    else:
        print("✅ Pagination already exists")
else:
    print("❌ admin_dashboard function not found")
