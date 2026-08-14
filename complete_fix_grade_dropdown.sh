#!/bin/bash

echo "========================================"
echo "  COMPLETE GRADE DROPDOWN FIX"
echo "========================================"

# 1. Verify forms.py is correct
echo "1. Checking forms.py..."
python -m py_compile core/forms.py && echo "   ✅ forms.py OK" || echo "   ❌ forms.py has errors"

# 2. Check grades in database
echo "2. Checking grades in database..."
python manage.py shell -c "from core.models import GradeLevel; grades = GradeLevel.objects.filter(is_active=True); print(f'   Found {grades.count()} active grades'); [print(f'     - {g.name} ({g.code})') for g in grades]"

# 3. Test StudentForm
echo "3. Testing StudentForm..."
python manage.py shell -c "from core.forms import StudentForm; f = StudentForm(); print(f'   Fields: {list(f.fields.keys())}'); print(f'   grade_level choices: {f.fields[\"grade_level\"].queryset.count() if \"grade_level\" in f.fields else 0}')"

echo ""
echo "✅ To complete the fix, manually add 'grade_levels' to the edit_student context in core/views.py"
echo "   Look for: context = {"
echo "   Add: 'grade_levels': grade_levels,"
echo ""
echo "Then restart the server: python manage.py runserver 5000"
