#!/usr/bin/env python3
import re

# Read the views.py file
with open('core/views.py', 'r') as f:
    content = f.read()

# Find the add_grade section and replace it
# The current code uses order_value from POST, we want to auto-assign
old_code = '''        elif action == "add_grade":
            try:
                order_value = int(request.POST.get("grade_order", 0))
            except (ValueError, TypeError):
                messages.error(request, "Grade order must be a whole number.")
                return redirect("core:school_setup")
            try:
                GradeLevel.objects.create(
                    school=school,
                    name=request.POST.get("grade_name", "").strip(),
                    code=request.POST.get("grade_code", "").strip(),
                    order=order_value,
                    is_active=True,
                )
                messages.success(request, "Grade level added!")
            except (ValueError, TypeError) as e:
                messages.error(request, f"Error adding grade: {e}")
            return redirect("core:school_setup")'''

new_code = '''        elif action == "add_grade":
            # Auto-assign order: next available number
            next_order = GradeLevel.objects.filter(school=school).count() + 1
            try:
                GradeLevel.objects.create(
                    school=school,
                    name=request.POST.get("grade_name", "").strip(),
                    code=request.POST.get("grade_code", "").strip(),
                    order=next_order,
                    is_active=True,
                )
                messages.success(request, f"Grade level added with order {next_order}!")
            except (ValueError, TypeError) as e:
                messages.error(request, f"Error adding grade: {e}")
            return redirect("core:school_setup")'''

# Replace in content
if old_code in content:
    content = content.replace(old_code, new_code)
    with open('core/views.py', 'w') as f:
        f.write(content)
    print("✅ Successfully patched views.py - grades will now auto-assign order numbers")
else:
    print("⚠️ Could not find the exact code pattern. Manual edit may be needed.")
    print("Look for 'elif action == \"add_grade\":' in core/views.py")
