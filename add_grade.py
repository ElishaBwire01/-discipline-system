#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import GradeLevel, School

def add_grade(name, code):
    school = School.objects.first()
    if not school:
        print("❌ No school found!")
        return False
    
    # Check if grade already exists
    if GradeLevel.objects.filter(school=school, name=name).exists():
        print(f"⚠️ Grade '{name}' already exists!")
        return False
    
    # Get next order number
    next_order = GradeLevel.objects.filter(school=school).count() + 1
    
    # Create the grade
    grade = GradeLevel.objects.create(
        school=school,
        name=name,
        code=code,
        order=next_order,
        is_active=True
    )
    
    print(f"✅ Added '{name}' as order {next_order}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  ADD GRADE/FORM")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("Usage: python add_grade.py 'Form Name' 'Code'")
        print("Example: python add_grade.py 'Form 7' 'F7'")
        sys.exit(1)
    
    name = sys.argv[1]
    code = sys.argv[2]
    school = School.objects.first()
    add_grade(name, code)
    
    # Show all grades
    print("\n📊 All grades:")
    for grade in GradeLevel.objects.filter(school=school).order_by('order'):
        print(f"  {grade.order}. {grade.name} ({grade.code})")
