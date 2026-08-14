#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import GradeLevel, School

def fix_grade_order():
    school = School.objects.first()
    if not school:
        print("❌ No school found. Please create a school first.")
        return
    
    # Get all grades ordered by order (ascending)
    grades = GradeLevel.objects.filter(school=school).order_by('order', 'id')
    
    if grades.count() == 0:
        print("📚 No grades found. Creating default grades...")
        default_grades = [
            {'name': 'Form 1', 'code': 'F1'},
            {'name': 'Form 2', 'code': 'F2'},
            {'name': 'Form 3', 'code': 'F3'},
            {'name': 'Form 4', 'code': 'F4'},
            {'name': 'Form 5', 'code': 'F5'},
            {'name': 'Form 6', 'code': 'F6'},
        ]
        for i, grade_data in enumerate(default_grades, start=1):
            GradeLevel.objects.create(
                school=school,
                name=grade_data['name'],
                code=grade_data['code'],
                order=i,
                is_active=True
            )
        print(f"✅ Created {len(default_grades)} default grades")
        grades = GradeLevel.objects.filter(school=school).order_by('order', 'id')
    
    print("\n📊 Current grades with order:")
    print("-" * 40)
    for grade in grades:
        print(f"  Order {grade.order}: {grade.name} ({grade.code})")
    
    # Reassign order based on current sequence
    print("\n🔄 Reassigning order numbers...")
    for index, grade in enumerate(grades, start=1):
        grade.order = index
        grade.save()
        print(f"  ✅ Set {grade.name} to order {index}")
    
    print("\n📊 Updated grades:")
    for grade in GradeLevel.objects.filter(school=school).order_by('order'):
        print(f"  Order {grade.order}: {grade.name} ({grade.code})")
    
    print(f"\n✅ Total grades: {GradeLevel.objects.filter(school=school).count()}")

if __name__ == "__main__":
    print("=" * 60)
    print("  FIX GRADE ORDER ASSIGNMENT")
    print("=" * 60)
    fix_grade_order()
