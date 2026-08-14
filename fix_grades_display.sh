#!/bin/bash

echo "========================================"
echo "  FIXING GRADES/FORMS DISPLAY"
echo "========================================"

# 1. Check if there's a school configured
python manage.py shell << 'PYTHON'
from core.models import School
school = School.objects.first()
if school:
    print(f"✅ School found: {school.name}")
else:
    print("❌ No school found. Creating default school...")
    from core.models import School
    school = School.objects.create(
        name="Default School",
        short_name="DS",
        current_year=2026,
        terms_per_year=3
    )
    print(f"✅ Created school: {school.name}")
PYTHON

# 2. Check grades
python manage.py shell << 'PYTHON'
from core.models import GradeLevel, School

school = School.objects.first()
if school:
    # Check if grades exist
    if GradeLevel.objects.filter(school=school).count() == 0:
        print("Creating default grades...")
        grades = [
            {'name': 'Form 1', 'code': 'F1', 'order': 1},
            {'name': 'Form 2', 'code': 'F2', 'order': 2},
            {'name': 'Form 3', 'code': 'F3', 'order': 3},
            {'name': 'Form 4', 'code': 'F4', 'order': 4},
            {'name': 'Form 5', 'code': 'F5', 'order': 5},
            {'name': 'Form 6', 'code': 'F6', 'order': 6},
        ]
        for grade_data in grades:
            GradeLevel.objects.get_or_create(
                school=school,
                name=grade_data['name'],
                defaults={
                    'code': grade_data['code'],
                    'order': grade_data['order'],
                    'is_active': True
                }
            )
        print(f"✅ Created {len(grades)} grades")
    else:
        print(f"✅ Grades already exist: {GradeLevel.objects.filter(school=school).count()}")
PYTHON

echo "✅ Fix complete!"
