import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Student, DisciplineReport, DisciplineCategory

# Get or create a sample report
try:
    student = Student.objects.first()
    teacher = User.objects.filter(is_superuser=False).first()
    category = DisciplineCategory.objects.first()
    
    if student and teacher and category:
        # Check if reports exist
        if DisciplineReport.objects.count() == 0:
            report = DisciplineReport.objects.create(
                student=student,
                reported_by=teacher,
                category=category,
                comments='Sample report for testing'
            )
            print(f"✅ Created sample report for {student.name}")
        else:
            print(f"ℹ️ Reports already exist: {DisciplineReport.objects.count()}")
    else:
        print("⚠️ Missing required data for sample report")
except Exception as e:
    print(f"⚠️ Could not create sample: {e}")
