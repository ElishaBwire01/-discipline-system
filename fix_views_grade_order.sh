#!/bin/bash

echo "========================================"
echo "  FIXING GRADE ORDER IN VIEWS.PY"
echo "========================================"

# Backup views.py
cp core/views.py core/views.py.backup_grade_fix

# Check if there's a grade add action in views.py
echo "🔍 Looking for grade add logic..."
grep -n "add_grade\|save_grade\|action.*grade" core/views.py

echo ""
echo "🔍 Looking for order assignment..."
grep -n "order" core/views.py | grep -i grade

echo ""
echo "📝 To fix: Add automatic order assignment when adding new grades"
echo "In the school_setup view, when adding a grade:"
echo ""
echo "  # Get the next order number"
echo "  next_order = GradeLevel.objects.filter(school=school).count() + 1"
echo "  grade = GradeLevel.objects.create("
echo "      school=school,"
echo "      name=grade_name,"
echo "      code=grade_code,"
echo "      order=next_order,"
echo "      is_active=True"
echo "  )"
