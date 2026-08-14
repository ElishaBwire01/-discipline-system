#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import GradeLevel, School
from core.forms import StudentForm

print("=" * 60)
print("  FIX GRADE DROPDOWNS")
print("=" * 60)

# Check school
school = School.objects.first()
if not school:
    print("❌ No school found! Creating one...")
    school = School.objects.create(
        name="Default School",
        short_name="DS",
        current_year=2026,
        terms_per_year=3
    )
    print(f"✅ Created school: {school.name}")

# Check grades
grades = GradeLevel.objects.filter(school=school, is_active=True).order_by('order')
print(f"\n📊 Grades in database: {grades.count()}")
for grade in grades:
    print(f"  - {grade.id}: {grade.name} ({grade.code}) - Order: {grade.order}")

# Check if grades exist in form
print("\n🔍 Checking StudentForm...")
form = StudentForm()
if 'grade' in form.fields:
    choices = list(form.fields['grade'].choices)
    print(f"  Grade field choices: {len(choices)} options")
    if len(choices) <= 1:
        print("  ⚠️ Grade dropdown is empty!")
        print("  This means the form's queryset is not getting grades.")
    else:
        print("  ✅ Grade dropdown has options")
else:
    print("  ❌ No 'grade' field in StudentForm")

print("\n✅ Check complete!")
