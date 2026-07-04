from core.models import Student, DisciplineCategory, DisciplineReport
from django.contrib.auth.models import User
import random

# Get admin
admin = User.objects.filter(is_superuser=True).first()
students = Student.objects.filter(is_active=True)
categories = DisciplineCategory.objects.filter(is_active=True)

if not categories:
    print("❌ No categories! Run: python manage.py seed_categories")
else:
    reports_added = 0
    for student in students[:5]:  # First 5 students
        for i in range(3):  # 3 reports each
            category = random.choice(categories)
            rating = random.choice(['VERY_MINOR', 'MINOR', 'MODERATE'])
            report = DisciplineReport.objects.create(
                student=student,
                reported_by=admin,
                category=category,
                comments=f"Sample report {i+1} for {student.name}",
                rating=rating
            )
            reports_added += 1
            print(f"✅ Report for {student.name}: {category.name} ({rating})")
    
    print(f"\n✅ {reports_added} reports added!")
    print(f"📊 Total reports: {DisciplineReport.objects.count()}")
