#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import GradeLevel, School

def ensure_proper_order():
    school = School.objects.first()
    if not school:
        print("❌ No school found.")
        return
    
    # Get all grades sorted by order
    grades = list(GradeLevel.objects.filter(school=school).order_by('order', 'id'))
    
    if not grades:
        print("📚 Creating default Form 1-6...")
        forms = ['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Form 5', 'Form 6']
        codes = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
        for i, (name, code) in enumerate(zip(forms, codes), start=1):
            GradeLevel.objects.create(
                school=school,
                name=name,
                code=code,
                order=i,
                is_active=True
            )
        grades = GradeLevel.objects.filter(school=school).order_by('order', 'id')
    
    # Display current order
    print("\n📊 Current Grades/Forms:")
    print("-" * 50)
    for grade in grades:
        print(f"  {grade.order}. {grade.name} ({grade.code})")
    print("-" * 50)
    
    # Fix order if needed
    print("\n🔧 Ensuring sequential order...")
    for index, grade in enumerate(grades, start=1):
        if grade.order != index:
            print(f"  Fixing {grade.name}: {grade.order} → {index}")
            grade.order = index
            grade.save()
    
    # Show final order
    print("\n✅ Final Grades/Forms Order:")
    print("-" * 50)
    for grade in GradeLevel.objects.filter(school=school).order_by('order'):
        print(f"  {grade.order}. {grade.name} ({grade.code})")
    print("-" * 50)
    print(f"✅ Total: {GradeLevel.objects.filter(school=school).count()} grades/forms")

if __name__ == "__main__":
    print("=" * 60)
    print("  GRADE/FORM ORDER FIX")
    print("=" * 60)
    ensure_proper_order()
